import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

import aiofiles
import pytest
import pytest_asyncio

from waterbowl.local_storage_service import (
    LogEntry,
    read_storage_log,
    save_to_storage_log,
    clear_local_storage,
)


@pytest_asyncio.fixture
def local_file_entries(test_picture) -> list[LogEntry]:
    yield [
        LogEntry(f"1.1,{test_picture}"),
        LogEntry(f"1.2,{test_picture}"),
        LogEntry(f"1.3,{test_picture}"),
    ]


@pytest_asyncio.fixture
def test_local_storage_dir() -> Path:
    with TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest_asyncio.fixture
async def test_log_file(test_local_storage_dir, local_file_entries) -> Path:
    log_file_location = test_local_storage_dir.joinpath("log.csv")
    async with aiofiles.open(log_file_location, "w+") as log_file:
        for log_entry in local_file_entries:
            await log_file.write(f"{log_entry.timestamp},{log_entry.picture}\n")
    yield log_file_location


@pytest_asyncio.fixture
def mock_local_storage(test_local_storage_dir, test_log_file):
    with mock.patch("waterbowl.local_storage_service.LOCAL_STORAGE_LOG", test_log_file):
        with mock.patch(
            "waterbowl.local_storage_service.LOCAL_STORAGE_DIR", test_local_storage_dir
        ):
            yield


@pytest.mark.usefixtures("mock_local_storage")
@pytest.mark.asyncio
async def test_read_local_storage(local_file_entries):
    async for log in read_storage_log():
        assert log in local_file_entries


@pytest.mark.usefixtures("mock_local_storage")
@pytest.mark.asyncio
async def test_save_to_local_storage(test_log_file, test_picture):
    with TemporaryDirectory() as tmp_dir:
        test_picture_src = Path(tmp_dir).joinpath("test_image.jpg")
        shutil.copy(test_picture, test_picture_src)
        await save_to_storage_log(timestamp=1.4, picture=test_picture_src)
        async with aiofiles.open(test_log_file, "r") as log_file:
            entries = await log_file.readlines()
        assert len(entries) == 4
        assert entries[3] == f"1.4,{test_picture.name}\n"


@pytest.mark.usefixtures("mock_local_storage")
@pytest.mark.asyncio
async def test_clear_local_storage(test_log_file, test_picture, test_local_storage_dir):
    test_picture_src = Path(test_local_storage_dir).joinpath("test_image.jpg")
    shutil.copy(test_picture, test_picture_src)

    assert len(list(test_local_storage_dir.glob("*.jpg"))) == 1
    async with aiofiles.open(test_log_file, "r") as log_file:
        entries = await log_file.readlines()
    assert len(entries) == 3

    await clear_local_storage()

    assert len(list(test_local_storage_dir.glob("*.jpg"))) == 0
    async with aiofiles.open(test_log_file, "r") as log_file:
        entries = await log_file.readlines()
    assert len(entries) == 0
