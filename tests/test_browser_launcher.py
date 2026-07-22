"""Unit tests for BrowserLauncher class.

Tests cover:
- Invalid browser type returns descriptive error with supported types listed
- LaunchResult captures success with load_time_ms
- LaunchResult captures failure with error_message

Requirements: 3.4, 3.5, 3.6
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from browser_automation.browser_launcher import BrowserLauncher, validate_browser_type
from browser_automation.models import BrowserType, LaunchResult


class TestInvalidBrowserTypeError:
    """Test that invalid browser type returns descriptive error with supported types listed.

    Validates: Requirements 3.6
    """

    def test_invalid_browser_type_raises_value_error(self):
        """Invalid browser type string raises ValueError."""
        with pytest.raises(ValueError):
            validate_browser_type("safari")

    def test_error_message_lists_all_supported_types(self):
        """Error message contains all supported browser types: chromium, edge, firefox."""
        with pytest.raises(ValueError) as exc_info:
            validate_browser_type("opera")

        error_message = str(exc_info.value)
        assert "chromium" in error_message
        assert "edge" in error_message
        assert "firefox" in error_message

    def test_error_message_includes_the_invalid_value(self):
        """Error message includes the invalid type that was provided."""
        with pytest.raises(ValueError) as exc_info:
            validate_browser_type("webkit")

        assert "webkit" in str(exc_info.value)

    def test_error_message_is_descriptive(self):
        """Error message is human-readable and descriptive."""
        with pytest.raises(ValueError) as exc_info:
            validate_browser_type("phantom")

        error_message = str(exc_info.value)
        # Should mention it's invalid and list supported types
        assert "Invalid browser type" in error_message or "invalid" in error_message.lower()
        assert "Supported" in error_message or "supported" in error_message.lower()


class TestLaunchResultSuccess:
    """Test that LaunchResult captures success with load_time_ms.

    Validates: Requirements 3.4, 3.5
    """

    def test_success_launch_result_has_load_time_ms(self):
        """A successful LaunchResult has a non-None load_time_ms."""
        result = LaunchResult(
            url="https://example.com",
            browser_type=BrowserType.CHROMIUM,
            instance_id=0,
            success=True,
            load_time_ms=150.5,
        )
        assert result.success is True
        assert result.load_time_ms == 150.5
        assert result.error_message is None

    def test_success_launch_result_load_time_is_positive(self):
        """A successful LaunchResult should have a positive load_time_ms."""
        result = LaunchResult(
            url="https://example.com",
            browser_type=BrowserType.EDGE,
            instance_id=1,
            success=True,
            load_time_ms=42.0,
        )
        assert result.load_time_ms > 0

    async def test_launch_browser_success_returns_load_time(self):
        """BrowserLauncher.launch_browser returns LaunchResult with load_time_ms on success.

        Validates: Requirements 3.4
        """
        launcher = BrowserLauncher()

        # Mock playwright internals
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.close = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_browser_type = AsyncMock()
        mock_browser_type.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_browser_type
        mock_pw.firefox = mock_browser_type

        # Patch async_playwright context manager at the source module
        mock_pw_ctx = AsyncMock()
        mock_pw_ctx.__aenter__ = AsyncMock(return_value=mock_pw)
        mock_pw_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_ctx,
        ):
            result = await launcher.launch_browser(
                url="https://example.com",
                browser_type=BrowserType.CHROMIUM,
                instance_id=0,
            )

        assert result.success is True
        assert result.load_time_ms is not None
        assert result.load_time_ms >= 0
        assert result.error_message is None
        assert result.url == "https://example.com"
        assert result.browser_type == BrowserType.CHROMIUM
        assert result.instance_id == 0


class TestLaunchResultFailure:
    """Test that LaunchResult captures failure with error_message.

    Validates: Requirements 3.5
    """

    def test_failure_launch_result_has_error_message(self):
        """A failed LaunchResult has a non-None error_message."""
        result = LaunchResult(
            url="https://unreachable.example.com",
            browser_type=BrowserType.FIREFOX,
            instance_id=1,
            success=False,
            error_message="Navigation timeout for firefox instance 1",
        )
        assert result.success is False
        assert result.error_message is not None
        assert "timeout" in result.error_message.lower()
        assert result.load_time_ms is None

    def test_failure_launch_result_preserves_context(self):
        """A failed LaunchResult preserves url, browser_type, and instance_id."""
        result = LaunchResult(
            url="https://broken.example.com",
            browser_type=BrowserType.EDGE,
            instance_id=2,
            success=False,
            error_message="Browser launch failed for edge instance 2",
        )
        assert result.url == "https://broken.example.com"
        assert result.browser_type == BrowserType.EDGE
        assert result.instance_id == 2

    async def test_launch_browser_failure_returns_error_message(self):
        """BrowserLauncher.launch_browser returns LaunchResult with error_message on failure.

        Validates: Requirements 3.5
        """
        launcher = BrowserLauncher()

        # Mock playwright to simulate a launch failure
        mock_browser_type = AsyncMock()
        mock_browser_type.launch = AsyncMock(
            side_effect=Exception("Browser binary not found")
        )

        mock_pw = MagicMock()
        mock_pw.chromium = mock_browser_type

        mock_pw_ctx = AsyncMock()
        mock_pw_ctx.__aenter__ = AsyncMock(return_value=mock_pw)
        mock_pw_ctx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "playwright.async_api.async_playwright",
            return_value=mock_pw_ctx,
        ):
            result = await launcher.launch_browser(
                url="https://example.com",
                browser_type=BrowserType.CHROMIUM,
                instance_id=0,
            )

        assert result.success is False
        assert result.error_message is not None
        assert "Browser binary not found" in result.error_message
        assert result.load_time_ms is None
        assert result.url == "https://example.com"
        assert result.browser_type == BrowserType.CHROMIUM
        assert result.instance_id == 0
