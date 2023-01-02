import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import pytest

from waterbowl.camera_service import (
    camera_service_factory,
    MockCameraService,
    CameraService,
)
from waterbowl.enums import Environments


@pytest.fixture
def mock_take_picture_sync(test_picture: Path):
    picture = test_picture

    def _mock(command: list[str]):
        shutil.copy(picture, command[2])

    with mock.patch("waterbowl.camera_service.take_picture_sync", _mock):
        yield


@pytest.mark.parametrize("environment", [Environments.PROD, Environments.DEV])
def test_factory(environment):
    with mock.patch("waterbowl.camera_service.ENVIRONMENT", environment):
        camera_service = camera_service_factory()
        if environment == Environments.PROD:
            assert camera_service == CameraService
        else:
            assert camera_service == MockCameraService


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_take_picture_sync")
async def test_take_picture_fails_on_existing_path(test_picture: Path):
    camera_service = CameraService()
    with pytest.raises(FileExistsError):
        await camera_service.take_picture(test_picture)


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_take_picture_sync")
async def test_take_picture():
    with TemporaryDirectory() as tmp_dir:
        camera_service = CameraService()
        new_file = await camera_service.take_picture(Path(tmp_dir).joinpath("new_file"))
        assert new_file.exists()
