import argparse

from src.log_reader import LogsHandlerService, ReportType


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Django logs.")
    parser.add_argument("files", nargs="+", help="List of Django log files to analyze.")
    parser.add_argument("--report", required=True, help="Report type to generate.")

    args = parser.parse_args()

    report_type = ReportType(args.report)
    service = LogsHandlerService(args.files)
    service()
    report = service.get_report(report_type)
    service.print_report(report)


if __name__ == "__main__":
    main()
