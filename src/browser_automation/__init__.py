"""Browser Automation Framework - Cross-browser testing with Playwright and asyncio."""

from browser_automation.browser_launcher import BrowserLauncher
from browser_automation.csv_reader import CSVReader
from browser_automation.execution_engine import ExecutionEngine
from browser_automation.logging_config import configure_logging
from browser_automation.models import (
    BrowserType,
    ExecutionConfig,
    ExecutionSummary,
    LaunchResult,
    ValidationResult,
)
from browser_automation.url_validator import URLValidator

__all__ = [
    "BrowserLauncher",
    "BrowserType",
    "CSVReader",
    "ExecutionConfig",
    "ExecutionEngine",
    "ExecutionSummary",
    "LaunchResult",
    "URLValidator",
    "ValidationResult",
    "configure_logging",
]
