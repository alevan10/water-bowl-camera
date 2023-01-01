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
    test_server.post(f"{base_url}/picture", status=200)
    success = await test_api_service.send_picture(timestamp=1.1, picture=Path(__file__))
    assert success


@pytest.mark.asyncio
async def test_send_picture_fails(
    base_url: str, test_api_service: ApiService, test_server: aioresponses
):
    test_server.post(f"{base_url}/picture", status=500, body="")
    with pytest.raises(ApiException):
        await test_api_service.send_picture(timestamp=1.1, picture=Path(__file__))
