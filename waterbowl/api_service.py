import json
from io import BytesIO
from pathlib import Path
from typing import Any

import aiofiles
import aiohttp
from aiohttp import FormData

from waterbowl.enums import API_BASE_URL


class ApiException(Exception):
    """
    An exception occurred in the water bowl api
    """


class ApiService:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url

    async def api_healthy(self) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as resp:
                return resp.status == 200

    async def send_picture(self, timestamp: float, picture: Path) -> str:
        form_data = FormData()
        form_data.add_field("timestamp", str(timestamp))
        async with aiofiles.open(picture, "rb") as picture_file:
            form_data.add_field(
                "picture",
                BytesIO(await picture_file.read()),
                filename=picture.name,
                content_type="image/jpeg",
            )
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/pictures/", data=form_data
                ) as resp:
                    if resp.status != 200:
                        raise ApiException(f"Error from the api: status {resp.status}")
                    picture_data = await resp.json()
                    return picture_data["id"]

    async def update_picture(
        self, picture_id: str, picture_data: dict[str, Any]
    ) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                f"{self.base_url}/pictures/{picture_id}/", json=picture_data
            ) as resp:
                if resp.status != 200:
                    raise ApiException(f"Error from the api: status {resp.status}")
        return True
