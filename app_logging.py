import logging
import os
from datetime import datetime


def setup_logging(log_dir=None):
    """Configure file and console logging and return the logger and log path."""
    log_dir = log_dir or os.getcwd()
    logs_dir = os.path.join(log_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    logger = logging.getLogger("DroneImageSort")
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)

    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log_file = os.path.join(
        logs_dir, f"drone_sort_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    logger.addHandler(console_handler)
    return logger, log_file


def log_sort_summary(logger, result):
    logger.info("=" * 50)
    logger.info("SORTING SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total files processed: {result.total_files}")
    logger.info(f"Moved to categories: {result.moved_to_categories} files")
    logger.info(f"Moved to Other: {result.moved_to_other} files")
    logger.info(f"Skipped: {result.skipped} files")
    logger.info(f"  Identical files skipped: {result.identical_skipped}")
    logger.info(f"Renamed due to name conflicts: {result.renamed} files")
    logger.info(f"Errors: {len(result.errors)}")
    logger.info("=" * 50)
