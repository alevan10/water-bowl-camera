from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator
from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from waterbowl.api_service import ApiException
from waterbowl.camera_service import AbstractCameraService, MockCameraService
from waterbowl.enums import TEST_FILE_LOCATION
from waterbowl.local_storage_service import LogEntry
from waterbowl.run_waterbowl_watcher import image_water_bowl


@pytest.fixture
def test_api_service() -> MagicMock:
    with mock.patch(
        "waterbowl.run_waterbowl_watcher.ApiService", MagicMock()
    ) as mock_api_service:
        yield mock_api_service


async def mock_storage_log():
    for line in [
        LogEntry(log_file_line=f"1.1,{TEST_FILE_LOCATION}"),
        LogEntry(log_file_line=f"1.1,{TEST_FILE_LOCATION}"),
    ]:
        yield line


@pytest.fixture
def mock_storage_functions(
    test_picture: Path,
) -> tuple[MagicMock, MagicMock, MagicMock]:
    with mock.patch(
        "waterbowl.run_waterbowl_watcher.read_storage_log", mock_storage_log
    ) as read_storage_log:
        with mock.patch(
            "waterbowl.run_waterbowl_watcher.save_to_storage_log",
            AsyncMock(return_value=test_picture),
        ) as save_to_storage_log:
            with mock.patch(
                "waterbowl.run_waterbowl_watcher.clear_local_storage",
                AsyncMock(return_value=True),
            ) as clear_local_storage:
                yield read_storage_log, save_to_storage_log, clear_local_storage


@pytest.fixture
def test_camera_service() -> AbstractCameraService:
    yield MockCameraService()


@pytest.mark.usefixtures("mock_local_storage_log", "mock_storage_functions")
@pytest.mark.asyncio
class TestImageWaterBowl:
    async def test_happy_path(
        self, test_api_service: MagicMock, test_camera_service: AbstractCameraService
    ):
        test_api_service.api_healthy = AsyncMock(return_value=True)
        test_api_service.send_picture = AsyncMock(return_value="picture_id")
        test_api_service.update_picture = AsyncMock(return_value=True)
        await image_water_bowl(cam=test_camera_service, api_service=test_api_service)

        test_api_service.api_healthy.assert_called_once()
        assert test_api_service.send_picture.call_count == 3

    @pytest.mark.freeze_time("2022-12-31")
    async def test_api_not_healthy(
        self,
        test_api_service: MagicMock,
        test_camera_service: AbstractCameraService,
        mock_storage_functions: tuple[MagicMock, MagicMock, MagicMock],
    ):
        _, mock_save_to_storage, _ = mock_storage_functions
        test_api_service.api_healthy = AsyncMock(return_value=False)
        await image_water_bowl(cam=test_camera_service, api_service=test_api_service)

        test_api_service.api_healthy.assert_called_once()
        mock_save_to_storage.assert_called_once()

        assert (
            mock_save_to_storage.call_args.kwargs.get("timestamp")
            == datetime.now().timestamp()
        )

    @pytest.mark.freeze_time("2022-12-31")
    async def test_api_throws_error(
        self,
        test_api_service: MagicMock,
        test_camera_service: AbstractCameraService,
        mock_storage_functions: tuple[MagicMock, MagicMock, MagicMock],
    ):
        _, mock_save_to_storage, _ = mock_storage_functions
        test_api_service.api_healthy = AsyncMock(side_effect=ApiException("womp womp"))
        await image_water_bowl(cam=test_camera_service, api_service=test_api_service)

        test_api_service.api_healthy.assert_called_once()
        mock_save_to_storage.assert_called_once()

        assert (
            mock_save_to_storage.call_args.kwargs.get("timestamp")
            == datetime.now().timestamp()
        )

    @pytest.mark.freeze_time("2022-12-31")
    async def test_read_from_log_if_exists(
        self,
        test_api_service: MagicMock,
        test_camera_service: AbstractCameraService,
        mock_storage_functions: tuple[
            AsyncGenerator[LogEntry, None], AsyncMock, AsyncMock
        ],
    ):
        read_storage_log, _, clear_local_storage = mock_storage_functions
        test_api_service.api_healthy = AsyncMock(return_value=True)
        test_api_service.send_picture = AsyncMock(return_value="picture_id")
        await image_water_bowl(cam=test_camera_service, api_service=test_api_service)

        test_api_service.api_healthy.assert_called_once()
        clear_local_storage.assert_called_once()
        assert test_api_service.send_picture.await_count == 3

    @pytest.mark.freeze_time("2022-12-31")
    async def test_with_default_update(
        self,
        test_api_service: MagicMock,
        test_camera_service: AbstractCameraService,
        mock_storage_functions: tuple[
            AsyncGenerator[LogEntry, None], AsyncMock, AsyncMock
        ],
    ):
        default = {"some": "data"}
        with patch("waterbowl.run_waterbowl_watcher.DEFAULT_PICTURE_METADATA", default):
            picture_id = "picture_id"
            read_storage_log, _, clear_local_storage = mock_storage_functions
            test_api_service.api_healthy = AsyncMock(return_value=True)
            test_api_service.send_picture = AsyncMock(return_value=picture_id)
            test_api_service.update_picture = AsyncMock(return_value=True)
            await image_water_bowl(
                cam=test_camera_service, api_service=test_api_service
            )

            test_api_service.update_picture.assert_called_once_with(
                picture_id=picture_id, picture_data=default
            )

    @pytest.mark.freeze_time("2022-12-31")
    async def test_with_no_default_update(
        self,
        test_api_service: MagicMock,
        test_camera_service: AbstractCameraService,
        mock_storage_functions: tuple[
            AsyncGenerator[LogEntry, None], AsyncMock, AsyncMock
        ],
    ):
        default = {}
        with patch("waterbowl.run_waterbowl_watcher.DEFAULT_PICTURE_METADATA", default):
            picture_id = "picture_id"
            read_storage_log, _, clear_local_storage = mock_storage_functions
            test_api_service.api_healthy = AsyncMock(return_value=True)
            test_api_service.send_picture = AsyncMock(return_value=picture_id)
            test_api_service.update_picture = AsyncMock(return_value=True)
            await image_water_bowl(
                cam=test_camera_service, api_service=test_api_service
            )

            test_api_service.update_picture.assert_not_called()
