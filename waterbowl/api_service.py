from io import BytesIO
from pathlib import Path

import aiofiles
import aiohttp
from aiohttp import FormData


class ApiException(Exception):
    """
    An exception occurred in the water bowl api
    """


class ApiService:
    def __init__(self, base_url: str = "http://levan.home/api/waterbowl/v1"):
        self.base_url = base_url

    async def api_healthy(self) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as resp:
                return resp.status == 200

    async def send_picture(self, timestamp: float, picture: Path) -> bool:
        form_data = FormData()
        form_data.add_field("timestamp", timestamp)
        async with aiofiles.open(picture, "rb") as picture_file:
            form_data.add_field(
                "picture",
                BytesIO(await picture_file.read()),
                filename=picture.name,
                content_type="image/jpeg",
            )
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/picture", data=form_data
                ) as resp:
                    if resp.status != 200:
                        raise ApiException()
                return True
