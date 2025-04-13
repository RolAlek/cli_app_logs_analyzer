import os
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import StrEnum
from typing import Sequence


class ReportType(StrEnum):
    HANDLERS = "handlers"


class LogLevel(StrEnum):
    INFO = "INFO"
    DEBUG = "DEBUG"
    WARN = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogsHandlerService:
    PATTERN: re.Pattern = re.compile(
        r"(?P<timestamp>[\d\-]+\s[\d:,]+) (?P<level>\w+) django\.request:.*?(?P<path>/[^\s]+)"
    )

    def __init__(self, logs_files: Sequence[str]):
        self._files = logs_files
        self._logs: list[str] = []

    def __call__(self):
        self._read_logs()

    def get_report(self, type_: ReportType) -> tuple[dict[str, dict[str, int]], int]:
        """Call's dispatcher report based on the specified type.

        Args:
            type_ (ReportType): The type of report to generate.
        """
        handlers = {ReportType.HANDLERS: self._get_handlers_report}
        if type_ not in handlers:
            raise ValueError(f"Invalid report type: {type_}")

        return handlers[type_]()

    @staticmethod
    def print_report(data: tuple[dict[str, dict[str, int]], int]) -> None:
        """Prints the report data.

        Args:
            data (tuple[dict[str, dict[str, int]], int]): A tuple containing:
                - A dictionary with handler paths as keys and another dictionary as values,
                which contains counts of requests at different logging levels.
                - An integer representing the total number of requests.
        """
        report_data, total_requests = data

        headers = ["HANDLER"] + [level.value for level in LogLevel]
        headers_row = f"{headers[0]:<20} " + " ".join(
            f"{header:<6}" for header in headers[1:]
        )

        print("=" * len(headers_row))
        print(f"{'Total Requests:':<20}{total_requests}")
        print("=" * len(headers_row))

        print(headers_row)
        print("-" * len(headers_row))

        for path, data in report_data.items():
            row = [path] + [data.get(level, 0) for level in LogLevel]
            print(f"{row[0]:<20} " + " ".join(f"{count:<8}" for count in row[1:]))

    def _get_handlers_report(self) -> tuple[dict[str, dict[str, int]], int]:
        """Generates a report on API handlers based on log entries.


        Args:
            logs (list[str]): A list of log entries to analyze.

        Returns:
            tuple[dict[str, dict[str, int]], int]: A tuple containing:
                - A dictionary with handler paths as keys and another dictionary as values,
                which contains counts of requests at different logging levels.
                - An integer representing the total number of requests.
        """
        data = defaultdict(lambda: defaultdict(int))
        requests_times = 0

        for log in self._logs:
            if "django.request" in log:
                log_match = self.PATTERN.search(log)

                if log_match:
                    level = log_match.group("level")
                    path = log_match.group("path")

                    data[path][level] += 1
                    requests_times += 1

        return data, requests_times

    def _read_log(self, path: str) -> list[str]:
        """Reads a log file and returns its contents.

        Args:
            path (str): The path of the log file to read.

        Raises:
            FileNotFoundError: If the specified file is not found.

        Returns:
            list[str]: A list of lines from the specified file.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        with open(path, "r", encoding="utf-8") as file:
            return file.readlines()

    def _read_logs(self) -> list[str]:
        """Reads logs from multiple files concurrently

        Returns:
            list[str]: A list of log entries from the specified files
        """
        logs = []

        with ThreadPoolExecutor() as executor:
            future_to_path = {
                executor.submit(self._read_log, path): path for path in self._files
            }

            for future in as_completed(future_to_path):
                path = future_to_path[future]

                logs.extend(future.result())

        self._logs = logs
