import json
from pathlib import Path

import pytest
from aioresponses import aioresponses

from waterbowl.api_service import ApiService, ApiException


@pytest.fixture
def base_url() -> str:
    yield "parakeet.jones/api"


@pytest.fixture
def test_server():
    with aioresponses() as mock_server:
        yield mock_server


@pytest.fixture
def test_api_service(base_url: str) -> ApiService:
    yield ApiService(base_url=base_url)


@pytest.mark.asyncio
async def test_get_health(
    base_url: str, test_api_service: ApiService, test_server: aioresponses
):
    test_server.get(f"{base_url}/health", status=200, body="")
    healthy = await test_api_service.api_healthy()
    assert healthy


@pytest.mark.asyncio
async def test_get_health_returns_false(
    base_url: str, test_api_service: ApiService, test_server: aioresponses
):
    test_server.get(f"{base_url}/health", status=500, body="")
    healthy = await test_api_service.api_healthy()
    assert not healthy


@pytest.mark.asyncio
async def test_send_picture(
    base_url: str, test_api_service: ApiService, test_server: aioresponses
):
    test_server.post(
        f"{base_url}/pictures", status=200, body=json.dumps({"id": "some_id"})
    )
    success = await test_api_service.send_picture(timestamp=1.1, picture=Path(__file__))
    assert success == "some_id"


@pytest.mark.asyncio
async def test_send_picture_fails(
    base_url: str, test_api_service: ApiService, test_server: aioresponses
):
    test_server.post(f"{base_url}/pictures", status=500, body="")
    with pytest.raises(ApiException):
        await test_api_service.send_picture(timestamp=1.1, picture=Path(__file__))


@pytest.mark.asyncio
async def test_update_picture(
    base_url: str, test_api_service: ApiService, test_server: aioresponses
):
    picture_id = "some_id"
    test_server.patch(f"{base_url}/pictures/{picture_id}/", status=200, body="")
    success = await test_api_service.update_picture(
        picture_id=picture_id, picture_data={}
    )
    assert success
