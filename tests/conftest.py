import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture
def root_dir() -> Path:
    yield Path(__file__).parent.parent


@pytest.fixture
def test_dir(root_dir: Path):
    yield root_dir.joinpath("tests")


@pytest.fixture
def test_data_dir(test_dir: Path):
    yield test_dir.joinpath("testdata")


@pytest.fixture
def mock_local_storage_dir() -> Path:
    with TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def mock_local_storage_log(mock_local_storage_dir: Path) -> Path:
    log_file = mock_local_storage_dir.joinpath("log.csv")
    log_file.touch()
    yield log_file


@pytest.fixture
def test_picture(test_data_dir: Path, mock_local_storage_dir: Path):
    tmp_file = mock_local_storage_dir.joinpath("test_image.jpg")
    shutil.copy(test_data_dir.joinpath("test_image.jpg"), tmp_file)
    yield tmp_file
