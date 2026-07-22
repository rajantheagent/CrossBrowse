"""Core data models and enums for the Browser Automation Framework."""

from dataclasses import dataclass, field
from enum import Enum


class BrowserType(Enum):
    """Supported browser types for automation."""

    CHROMIUM = "chromium"
    EDGE = "edge"
    FIREFOX = "firefox"


@dataclass(frozen=True)
class ValidationResult:
    """Result of URL validation containing valid and invalid entries."""

    valid_urls: list[str]
    invalid_entries: list[tuple[str, str]]  # (url, reason)


@dataclass(frozen=True)
class LaunchResult:
    """Result of a single browser launch attempt."""

    url: str
    browser_type: BrowserType
    instance_id: int
    success: bool
    error_message: str | None = None
    load_time_ms: float | None = None


@dataclass(frozen=True)
class ExecutionConfig:
    """Configuration for the execution engine."""

    concurrency_limit: int | None = None  # None means unlimited
    browsers_per_url: dict[BrowserType, int] = field(
        default_factory=lambda: {
            BrowserType.CHROMIUM: 2,
            BrowserType.EDGE: 2,
            BrowserType.FIREFOX: 2,
        }
    )


@dataclass(frozen=True)
class ExecutionSummary:
    """Summary of a complete execution run."""

    total_tasks: int
    successful: int
    failed: int
    results: list[LaunchResult]
