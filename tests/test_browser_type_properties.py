"""Property-based tests for browser type validation.

Feature: browser-automation-framework, Property 7: Invalid browser type produces error
"""

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from browser_automation.browser_launcher import validate_browser_type


# Supported browser types that must be excluded from generated strings
SUPPORTED_TYPES = {"chromium", "edge", "firefox"}


# Strategy: generate random strings that are NOT valid browser types
invalid_browser_type_strategy = st.text(
    min_size=0,
    max_size=50,
).filter(lambda s: s not in SUPPORTED_TYPES)


@settings(max_examples=100)
@given(browser_type_str=invalid_browser_type_strategy)
def test_invalid_browser_type_produces_error(browser_type_str):
    """Property 7: Invalid browser type produces error

    For any string that is not one of "chromium", "edge", or "firefox",
    the Browser_Launcher SHALL return an error message that contains
    all three supported browser type names.

    **Validates: Requirements 3.6**
    """
    # Act & Assert: must raise ValueError
    with pytest.raises(ValueError) as exc_info:
        validate_browser_type(browser_type_str)

    # Assert: error message contains all three supported browser type names
    error_message = str(exc_info.value)
    assert "chromium" in error_message, (
        f"Error message missing 'chromium': {error_message}"
    )
    assert "edge" in error_message, (
        f"Error message missing 'edge': {error_message}"
    )
    assert "firefox" in error_message, (
        f"Error message missing 'firefox': {error_message}"
    )
