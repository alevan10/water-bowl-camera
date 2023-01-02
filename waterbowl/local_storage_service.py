import os
import shutil
from pathlib import Path
from typing import AsyncGenerator

import aiofiles

from waterbowl.enums import LOCAL_STORAGE_DIR, LOCAL_STORAGE_LOG


class LogEntry:
    def __init__(self, log_file_line: str):
        split_line = log_file_line.strip("\n").split(",")
        self.timestamp = float(split_line[0])
        self.picture = LOCAL_STORAGE_DIR.joinpath(split_line[1])

    def __eq__(self, other: "LogEntry"):
        return self.timestamp == other.timestamp and self.picture == other.picture


async def read_storage_log() -> AsyncGenerator[LogEntry, None]:
    LOCAL_STORAGE_LOG.touch(exist_ok=True)
    async with aiofiles.open(LOCAL_STORAGE_LOG, "r") as log_file:
        while line := await log_file.readline():
            yield LogEntry(line)


async def save_to_storage_log(timestamp: float, picture: Path) -> Path:
    LOCAL_STORAGE_LOG.touch(exist_ok=True)
    async with aiofiles.open(LOCAL_STORAGE_LOG, "a") as log_file:
        await log_file.write(f"{timestamp},{picture.name}\n")
    new_location = LOCAL_STORAGE_DIR.joinpath(picture.name)
    shutil.move(picture, new_location)
    return new_location


async def clear_local_storage() -> None:
    async with aiofiles.open(LOCAL_STORAGE_LOG, "w") as log_file:
        await log_file.truncate(0)
    for file in LOCAL_STORAGE_DIR.glob("*.jpg"):
        os.unlink(file)
