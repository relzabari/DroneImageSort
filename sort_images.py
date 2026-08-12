import argparse
import os

from app_logging import log_sort_summary, setup_logging
from sorting_engine import sort_drone_images


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Sort drone files into Thermal, Visual, Wide, and Other folders."
    )
    parser.add_argument("source_folder", help="Folder containing the files to sort")
    parser.add_argument(
        "destination_folder",
        nargs="?",
        help="Destination folder (defaults to the source folder)",
    )
    args = parser.parse_args(argv)

    requested_log_dir = args.destination_folder or args.source_folder
    log_dir = requested_log_dir if os.path.isdir(requested_log_dir) else os.getcwd()
    logger, log_file = setup_logging(log_dir)
    logger.info("DroneImageSort started")
    logger.info(f"Log file: {log_file}")

    result = sort_drone_images(
        args.source_folder,
        args.destination_folder,
        progress=lambda level, message: getattr(logger, level)(message),
    )
    log_sort_summary(logger, result)
    if result.success:
        logger.info("DroneImageSort completed successfully")
        return 0

    logger.error("DroneImageSort completed with errors")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
