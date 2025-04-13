import pytest
from faker import Faker

from src.log_reader import LogLevel, LogsHandlerService, ReportType


def test_invalid_report_type(logs_handler_service: LogsHandlerService):
    with pytest.raises(ValueError):
        logs_handler_service.get_report("INVALID_TYPE")


def test_read_log_success(get_log_file: str):
    service = LogsHandlerService([get_log_file])

    assert len(service._files) > 0

    service()

    assert len(service._logs) == 5
    assert isinstance(service._logs[0], str)


def test_read_logs_from_multiple_files_success(get_log_files: list[str]):
    service = LogsHandlerService(get_log_files)

    assert len(service._files) == 2

    service()

    assert len(service._logs) == 10


def test_read_logs_fail_from_invalid_path(faker: Faker):
    fake_path = faker.file_path()
    service = LogsHandlerService([fake_path])

    with pytest.raises(FileNotFoundError) as exc_info:
        service()

    assert str(exc_info.value) == f"File not found: {fake_path}"
    assert len(service._logs) == 0


def test_get_handlers_report_fail_with_invalid_type(
    logs_handler_service: LogsHandlerService,
    faker: Faker,
):
    invalid_type = faker.word()
    with pytest.raises(ValueError) as exc_info:
        logs_handler_service.get_report(invalid_type)

    assert str(exc_info.value) == f"Invalid report type: {invalid_type}"


def test_get_handlers_report_success(logs_handler_service: LogsHandlerService):
    report = logs_handler_service.get_report(ReportType.HANDLERS)

    assert isinstance(report, tuple)
    assert isinstance(report[0], dict)

    for key, value in report[0]["/api/v1/resource"].items():
        assert key in [level.value for level in LogLevel]
        assert value == 1

    assert isinstance(report[1], int)
    assert report[1] == 5
