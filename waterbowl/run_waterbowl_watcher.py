import asyncio
import logging
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from waterbowl.api_service import ApiException, ApiService
from waterbowl.camera_service import AbstractCameraService, camera_service_factory
from waterbowl.enums import LOCAL_STORAGE_DIR, WAIT_TIME
from waterbowl.local_storage_service import (
    clear_local_storage,
    read_storage_log,
    save_to_storage_log,
)

logger = logging.getLogger(__name__)


async def image_water_bowl(cam: AbstractCameraService, api_service: ApiService) -> None:
    now_timestamp = datetime.now().timestamp()
    with TemporaryDirectory() as tmp_dir:
        try:
            new_file: Path = await cam.take_picture(
                Path(tmp_dir).joinpath(f"{now_timestamp}.jpg")
            )
            # First, check that the api is active and ready for use
            if not await api_service.api_healthy():
                new_file = await save_to_storage_log(
                    timestamp=now_timestamp, picture=new_file
                )
                logger.error(
                    "API service not healthy, caching file for later",
                    extra={"timestamp": now_timestamp, "picture": new_file},
                )
            else:
                # If the API is ready, check for any previously cached requests to send first
                async for log_entry in read_storage_log():
                    logger.debug(
                        "Log entry found, attempting to send",
                        extra={
                            "timestamp": log_entry.timestamp,
                            "picture": log_entry.picture,
                        },
                    )
                    await api_service.send_picture(
                        timestamp=log_entry.timestamp, picture=log_entry.picture
                    )
                # Clear the local storage just in case we had some entries to send
                await clear_local_storage()
                # Then, send the new picture
                await api_service.send_picture(
                    timestamp=now_timestamp, picture=new_file
                )
        except ApiException as ex:
            new_file = await save_to_storage_log(
                timestamp=now_timestamp, picture=new_file
            )
            logger.error(
                "API exception received, caching file for later",
                extra={"timestamp": now_timestamp, "picture": new_file, "error": ex},
            )
        except Exception as ex:
            new_file = await save_to_storage_log(
                timestamp=now_timestamp, picture=new_file
            )
            logger.error(
                "Unexpected error occurred, caching file for later",
                extra={"timestamp": now_timestamp, "picture": new_file, "error": ex},
            )
        finally:
            new_file.unlink(missing_ok=True)


async def watch_water_bowl():
    camera_service: AbstractCameraService = camera_service_factory()()
    api_service = ApiService()
    LOCAL_STORAGE_DIR.mkdir(exist_ok=True)
    while True:
        await image_water_bowl(camera_service, api_service)
        await asyncio.sleep(WAIT_TIME)
    pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(watch_water_bowl())
