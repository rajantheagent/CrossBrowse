"""Property-based tests for failure isolation in ExecutionEngine.

Feature: browser-automation-framework, Property 10: Failure isolation
"""

import asyncio
from unittest.mock import AsyncMock

from hypothesis import given, settings
from hypothesis import strategies as st

from browser_automation.browser_launcher import BrowserLauncher
from browser_automation.execution_engine import ExecutionEngine
from browser_automation.models import BrowserType, ExecutionConfig, LaunchResult


# Strategy: generate a list of 1-5 valid URLs
url_strategy = st.lists(
    st.sampled_from([
        "https://example.com",
        "https://test.org",
        "https://demo.net",
        "https://site.io",
        "https://app.dev",
    ]),
    min_size=1,
    max_size=5,
    unique=True,
)


@settings(max_examples=100)
@given(
    urls=url_strategy,
    data=st.data(),
)
def test_failure_isolation(urls, data):
    """Property 10: Failure isolation

    For any set of tasks where a subset fails, the ExecutionEngine SHALL
    still execute all remaining non-failing tasks to completion, and the
    execution summary SHALL contain results for every task (both successful
    and failed).

    **Validates: Requirements 6.5, 7.4**
    """
    num_urls = len(urls)
    total_tasks = num_urls * 6  # 6 tasks per URL (2 chromium + 2 edge + 2 firefox)

    # Generate a random set of task indices that should fail (0 to total_tasks-1)
    fail_indices = data.draw(
        st.frozensets(
            st.integers(min_value=0, max_value=total_tasks - 1),
            min_size=0,
            max_size=total_tasks,
        )
    )

    # Build the task matrix in the same order as ExecutionEngine._generate_task_matrix
    task_matrix: list[tuple[str, BrowserType, int]] = []
    browsers_per_url = {
        BrowserType.CHROMIUM: 2,
        BrowserType.EDGE: 2,
        BrowserType.FIREFOX: 2,
    }
    for url in urls:
        for browser_type, count in browsers_per_url.items():
            for instance_id in range(count):
                task_matrix.append((url, browser_type, instance_id))

    # Track call order to determine which index each call corresponds to
    call_counter = {"count": 0}

    async def mock_launch_browser(
        url: str, browser_type: BrowserType, instance_id: int
    ) -> LaunchResult:
        """Mock launcher that fails for tasks at designated fail indices."""
        idx = call_counter["count"]
        call_counter["count"] += 1

        if idx in fail_indices:
            raise Exception(f"Simulated failure for task index {idx}")

        return LaunchResult(
            url=url,
            browser_type=browser_type,
            instance_id=instance_id,
            success=True,
            load_time_ms=100.0,
        )

    # Create mock launcher
    launcher = BrowserLauncher()
    launcher.launch_browser = mock_launch_browser  # type: ignore[method-assign]

    # Create engine with concurrency_limit=10
    config = ExecutionConfig(concurrency_limit=10)
    engine = ExecutionEngine(config=config, launcher=launcher)

    # Execute
    summary = asyncio.run(engine.execute(urls))

    # Assert total_tasks matches expected
    assert summary.total_tasks == total_tasks, (
        f"Expected total_tasks={total_tasks}, got {summary.total_tasks}"
    )

    # Assert every task has a result
    assert len(summary.results) == total_tasks, (
        f"Expected {total_tasks} results, got {len(summary.results)}"
    )

    # Assert failed tasks have success=False and non-failing tasks have success=True
    for i, result in enumerate(summary.results):
        if i in fail_indices:
            assert result.success is False, (
                f"Task at index {i} was expected to fail but succeeded"
            )
            assert result.error_message is not None, (
                f"Task at index {i} failed but has no error_message"
            )
        else:
            assert result.success is True, (
                f"Task at index {i} was expected to succeed but failed: "
                f"{result.error_message}"
            )

    # Assert summary counts are consistent
    assert summary.successful + summary.failed == total_tasks
    assert summary.failed == len(fail_indices)
    assert summary.successful == total_tasks - len(fail_indices)
