import os
from pathlib import Path
from typing import Generator

import pytest

from src.log_reader import LogsHandlerService

BASE_DIR = Path(__file__).parent.parent
READ_DATA = [
    "2023-10-01 12:00:00 INFO django.request: GET /api/v1/resource\n",
    "2023-10-01 12:01:00 DEBUG django.request: POST /api/v1/resource\n",
    "2023-10-01 12:02:00 WARNING django.request: GET /api/v1/resource\n",
    "2023-10-01 12:03:00 ERROR django.request: GET /api/v1/resource\n",
    "2023-10-01 12:03:00 CRITICAL django.request: GET /api/v1/resource\n",
]


@pytest.fixture
def get_log_file() -> Generator[str, None]:
    log_file_path = BASE_DIR / "test.log"

    with open(log_file_path, "w", encoding="utf-8") as file:
        for data in READ_DATA:
            file.write(data)

    yield str(log_file_path)

    os.remove(log_file_path)


@pytest.fixture
def get_log_files() -> Generator[list[str], None]:
    paths = []

    for index in range(1, 3):
        with open(BASE_DIR / f"test_{index}.log", "w", encoding="utf-8") as file:
            for data in READ_DATA:
                file.write(data)

            paths.append(str(file.name))

    yield paths

    for path in paths:
        os.remove(path)


@pytest.fixture
def logs_handler_service(get_log_file: str) -> LogsHandlerService:
    service = LogsHandlerService([get_log_file])
    service()
    return service
