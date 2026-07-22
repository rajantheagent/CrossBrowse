"""Unit tests for browser type validation in BrowserLauncher."""

import pytest

from browser_automation.browser_launcher import validate_browser_type
from browser_automation.models import BrowserType


class TestValidateBrowserType:
    """Tests for the validate_browser_type function."""

    def test_valid_chromium(self):
        """Test that 'chromium' returns BrowserType.CHROMIUM."""
        result = validate_browser_type("chromium")
        assert result == BrowserType.CHROMIUM

    def test_valid_edge(self):
        """Test that 'edge' returns BrowserType.EDGE."""
        result = validate_browser_type("edge")
        assert result == BrowserType.EDGE

    def test_valid_firefox(self):
        """Test that 'firefox' returns BrowserType.FIREFOX."""
        result = validate_browser_type("firefox")
        assert result == BrowserType.FIREFOX

    def test_invalid_type_raises_value_error(self):
        """Test that an invalid browser type raises ValueError."""
        with pytest.raises(ValueError):
            validate_browser_type("safari")

    def test_invalid_type_error_message_contains_all_supported_types(self):
        """Test that the error message includes all three supported browser types."""
        with pytest.raises(ValueError, match="chromium") as exc_info:
            validate_browser_type("invalid_browser")

        error_message = str(exc_info.value)
        assert "chromium" in error_message
        assert "edge" in error_message
        assert "firefox" in error_message

    def test_invalid_type_error_message_contains_invalid_value(self):
        """Test that the error message includes the invalid value provided."""
        with pytest.raises(ValueError) as exc_info:
            validate_browser_type("opera")

        error_message = str(exc_info.value)
        assert "opera" in error_message

    def test_empty_string_raises_value_error(self):
        """Test that an empty string raises ValueError with supported types."""
        with pytest.raises(ValueError) as exc_info:
            validate_browser_type("")

        error_message = str(exc_info.value)
        assert "chromium" in error_message
        assert "edge" in error_message
        assert "firefox" in error_message

    def test_case_sensitive_validation(self):
        """Test that validation is case-sensitive (uppercase not accepted)."""
        with pytest.raises(ValueError):
            validate_browser_type("Chromium")

        with pytest.raises(ValueError):
            validate_browser_type("FIREFOX")
