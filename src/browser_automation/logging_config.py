"""Logging configuration for the Browser Automation Framework."""

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """Configure logging for the Browser Automation Framework.

    Sets up structured log format with timestamp, level, module name, and message.
    Outputs to stderr so it doesn't interfere with stdout data output.

    Log level guidance:
        - ERROR: Fatal failures that halt execution or individual task failures
        - WARNING: Skipped items (invalid URLs, failed browser instances)
        - INFO: Normal execution flow (task start/complete, summary)
        - DEBUG: Detailed execution state (semaphore acquisition, context lifecycle)

    Args:
        level: Logging level string (DEBUG, INFO, WARNING, ERROR).
    """
    log_format = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    # Set the root logger for the package
    package_logger = logging.getLogger("browser_automation")
    package_logger.setLevel(numeric_level)
