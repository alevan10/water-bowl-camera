import shutil
from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest

from waterbowl.api_service import ApiService
from waterbowl.camera_service import MockCameraService, AbstractCameraService
from waterbowl.run_waterbowl_watcher import image_water_bowl


@pytest.fixture
def test_camera_service() -> AbstractCameraService:
    yield MockCameraService()


@pytest.fixture
def test_api_service() -> ApiService:
    yield ApiService()


@pytest.fixture
def mock_local_storage_log(mock_local_storage_dir: Path) -> Path:
    log_file = mock_local_storage_dir.joinpath("log.csv")
    log_file.touch()
    yield log_file


@pytest.fixture
def mock_local_storage(
    mock_local_storage_dir: Path, mock_local_storage_log: Path
) -> None:
    with mock.patch(
        "waterbowl.run_waterbowl_watcher.LOCAL_STORAGE_DIR", mock_local_storage_dir
    ):
        with mock.patch(
            "waterbowl.local_storage_service.LOCAL_STORAGE_DIR", mock_local_storage_dir
        ):
            with mock.patch(
                "waterbowl.local_storage_service.LOCAL_STORAGE_LOG",
                mock_local_storage_log,
            ):
                yield


@pytest.fixture
def test_stored_pictures(
    mock_local_storage_dir: Path, mock_local_storage_log: Path, test_picture: Path
) -> list[Path]:
    timestamp_1 = datetime.now().timestamp()
    timestamp_2 = datetime.now().timestamp()
    file_1 = mock_local_storage_dir.joinpath(f"{timestamp_1}.jpg")
    file_2 = mock_local_storage_dir.joinpath(f"{timestamp_2}.jpg")
    shutil.copy(test_picture, file_1)
    shutil.copy(test_picture, file_2)
    with open(mock_local_storage_log, "w") as log_file:
        log_file.writelines(
            [f"{timestamp_1},{file_1.name}\n", f"{timestamp_2},{file_2.name}\n"]
        )
    yield file_1, file_2


class TestImageWaterBowl:
    @pytest.mark.asyncio
    @pytest.mark.usefixtures("mock_local_storage")
    async def test_image_water_bowl_success(
        self, test_camera_service: AbstractCameraService, test_api_service: ApiService
    ):
        result = await image_water_bowl(
            cam=test_camera_service, api_service=test_api_service
        )
        assert result is True

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("mock_local_storage", "test_stored_pictures")
    async def test_image_water_bowl_success_with_log_entries(
        self, test_camera_service: AbstractCameraService, test_api_service: ApiService
    ):
        result = await image_water_bowl(
            cam=test_camera_service, api_service=test_api_service
        )
        assert result is True
