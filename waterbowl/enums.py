import os
from enum import Enum
from pathlib import Path


class Environments(str, Enum):
    PROD = "prod"
    DEV = "dev"


API_BASE_URL = os.environ.get("API_BASE_URL", "http://levan.home/api/waterbowl/v1")
ENVIRONMENT = os.environ.get("ENVIRONMENT", Environments.DEV)
WAIT_TIME = os.environ.get("WAIT_TIME", 15 * 60)  # Wait for 15 minutes

ROOT_DIR = Path(__file__).parent.parent
TEST_FILE_NAME = "test_image.jpg"
WATERBOWL_DIR = ROOT_DIR.joinpath("waterbowl")
TEST_FILE_LOCATION = WATERBOWL_DIR.joinpath(TEST_FILE_NAME)
LOCAL_STORAGE_DIR = Path(
    os.environ.get("LOCAL_STORAGE_DIR", ROOT_DIR.joinpath("local"))
)
LOCAL_STORAGE_LOG = Path(
    os.environ.get("LOCAL_STORAGE_LOG", LOCAL_STORAGE_DIR.joinpath("log.csv"))
)
