"""Property-based tests for invalid concurrency limit rejection.

Feature: browser-automation-framework, Property 11: Invalid concurrency limit rejection
"""

from unittest.mock import AsyncMock

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from browser_automation.execution_engine import ExecutionEngine
from browser_automation.models import ExecutionConfig


# Strategy: generate integers outside the valid range [1, 50]
# Either <= 0 (negative or zero) or >= 51
invalid_concurrency_limit_strategy = st.one_of(
    st.integers(max_value=0),
    st.integers(min_value=51),
)


@settings(max_examples=100)
@given(limit=invalid_concurrency_limit_strategy)
def test_invalid_concurrency_limit_rejection(limit):
    """Property 11: Invalid concurrency limit rejection

    For any integer value less than 1 or greater than 50 provided as a
    concurrency limit, the Execution_Engine SHALL raise a ValueError with
    a message indicating the valid range.

    **Validates: Requirements 6.6**
    """
    # Arrange: create config with invalid concurrency limit
    config = ExecutionConfig(concurrency_limit=limit)
    mock_launcher = AsyncMock()

    # Act & Assert: must raise ValueError
    with pytest.raises(ValueError) as exc_info:
        ExecutionEngine(config, mock_launcher)

    # Assert: error message indicates valid range [1, 50]
    error_message = str(exc_info.value)
    assert "1" in error_message, (
        f"Error message should mention minimum value '1': {error_message}"
    )
    assert "50" in error_message, (
        f"Error message should mention maximum value '50': {error_message}"
    )
