import asyncio
import shutil
import subprocess
import logging
from abc import ABC, abstractmethod
from pathlib import Path

from waterbowl.enums import ENVIRONMENT, ROOT_DIR, Environments

TEST_FILE = ROOT_DIR.joinpath("tests", "testdata", "test_image.jpg")

logger = logging.getLogger(__name__)


def take_picture_sync(command: list[str]) -> None:
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    while True:
        return_code = process.poll()
        if return_code or return_code == 0:
            print("RETURN CODE", return_code)
            # Process has finished, read rest of the output
            for output in process.stdout.readlines():
                print(output.strip())
            break


class AbstractCameraService(ABC):

    picture_command: list[str] = []

    @abstractmethod
    def __init__(self):
        raise NotImplementedError()

    @abstractmethod
    async def take_picture(self, filepath: Path) -> Path:
        raise NotImplementedError()


class MockCameraService(AbstractCameraService):

    picture_command: list[str] = ["echo", "squak"]

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def take_picture(self, filepath: Path) -> Path:
        if filepath.exists():
            raise FileExistsError()
        await self.loop.run_in_executor(None, take_picture_sync, self.picture_command)
        await self.loop.run_in_executor(None, shutil.copy, TEST_FILE, filepath)
        return filepath


class CameraCaptureError(Exception):
    """
    Raised if there is an error when capturing an image.
    """


class CameraService(AbstractCameraService):

    picture_command: list[str] = ["libcamera-still", "-o"]

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def take_picture(self, filepath: Path) -> Path:
        logger.info("Taking picture.", extra={"picture_file": filepath})
        if filepath.exists():
            raise FileExistsError()
        command = [*self.picture_command, str(filepath)]
        await self.loop.run_in_executor(None, take_picture_sync, command)
        if not filepath.exists():
            raise CameraCaptureError()
        return filepath


def camera_service_factory() -> type[AbstractCameraService]:
    if ENVIRONMENT == Environments.PROD:
        return CameraService
    return MockCameraService
