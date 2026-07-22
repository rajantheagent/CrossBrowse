"""Unit tests for ExecutionEngine.

Tests concurrency limit validation and task matrix generation.
Validates: Requirements 6.3, 6.4, 6.6, 7.1, 7.2
"""

from unittest.mock import MagicMock

import pytest

from browser_automation.execution_engine import ExecutionEngine
from browser_automation.models import BrowserType, ExecutionConfig


@pytest.fixture
def mock_launcher():
    """Create a mock BrowserLauncher for testing."""
    return MagicMock()


class TestConcurrencyLimitValidation:
    """Tests for concurrency limit validation (Requirements 6.3, 6.6)."""

    def test_concurrency_limit_zero_raises_value_error(self, mock_launcher):
        """Concurrency limit of 0 should raise ValueError."""
        config = ExecutionConfig(concurrency_limit=0)
        with pytest.raises(ValueError, match="between 1 and 50"):
            ExecutionEngine(config, mock_launcher)

    def test_concurrency_limit_51_raises_value_error(self, mock_launcher):
        """Concurrency limit of 51 should raise ValueError."""
        config = ExecutionConfig(concurrency_limit=51)
        with pytest.raises(ValueError, match="between 1 and 50"):
            ExecutionEngine(config, mock_launcher)

    def test_concurrency_limit_1_is_accepted(self, mock_launcher):
        """Concurrency limit of 1 (lower bound) should be accepted."""
        config = ExecutionConfig(concurrency_limit=1)
        engine = ExecutionEngine(config, mock_launcher)
        assert engine.config.concurrency_limit == 1

    def test_concurrency_limit_50_is_accepted(self, mock_launcher):
        """Concurrency limit of 50 (upper bound) should be accepted."""
        config = ExecutionConfig(concurrency_limit=50)
        engine = ExecutionEngine(config, mock_launcher)
        assert engine.config.concurrency_limit == 50

    def test_none_concurrency_limit_means_unlimited(self, mock_launcher):
        """None concurrency limit should be accepted (means unlimited)."""
        config = ExecutionConfig(concurrency_limit=None)
        engine = ExecutionEngine(config, mock_launcher)
        assert engine.config.concurrency_limit is None


class TestTaskMatrixGeneration:
    """Tests for task matrix generation (Requirements 6.4, 7.1, 7.2)."""

    def test_single_url_generates_exactly_6_tasks(self, mock_launcher):
        """A single URL should produce exactly 6 tasks (2 per browser type)."""
        config = ExecutionConfig()
        engine = ExecutionEngine(config, mock_launcher)

        tasks = engine._generate_task_matrix(["https://example.com"])

        assert len(tasks) == 6
        # Verify 2 chromium, 2 edge, 2 firefox
        chromium_tasks = [t for t in tasks if t[1] == BrowserType.CHROMIUM]
        edge_tasks = [t for t in tasks if t[1] == BrowserType.EDGE]
        firefox_tasks = [t for t in tasks if t[1] == BrowserType.FIREFOX]
        assert len(chromium_tasks) == 2
        assert len(edge_tasks) == 2
        assert len(firefox_tasks) == 2

    def test_multiple_urls_generate_n_times_6_tasks(self, mock_launcher):
        """N URLs should produce N × 6 tasks."""
        config = ExecutionConfig()
        engine = ExecutionEngine(config, mock_launcher)

        urls = [
            "https://example.com",
            "https://test.org",
            "https://demo.io",
        ]
        tasks = engine._generate_task_matrix(urls)

        assert len(tasks) == 3 * 6  # 18 tasks total
        # Each URL should have exactly 6 tasks
        for url in urls:
            url_tasks = [t for t in tasks if t[0] == url]
            assert len(url_tasks) == 6
