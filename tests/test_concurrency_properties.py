"""Property-based tests for concurrency limit enforcement.

Feature: browser-automation-framework, Property 9: Concurrency limit enforcement
"""

import asyncio

from hypothesis import given, settings
from hypothesis import strategies as st
import pytest

from browser_automation.execution_engine import ExecutionEngine
from browser_automation.models import (
    BrowserType,
    ExecutionConfig,
    LaunchResult,
)


@settings(max_examples=100, deadline=None)
@given(
    concurrency_limit=st.integers(min_value=1, max_value=50),
    url_count=st.integers(min_value=1, max_value=10),
)
def test_concurrency_limit_enforcement(concurrency_limit, url_count):
    """Property 9: Concurrency limit enforcement

    For any concurrency limit L (where 1 <= L <= 50) and any number of tasks,
    the Execution_Engine SHALL never have more than L tasks executing
    simultaneously at any point during execution.

    **Validates: Requirements 6.3, 7.3**
    """

    async def run_test():
        # Track concurrent execution
        current_concurrent = 0
        max_concurrent = 0
        lock = asyncio.Lock()

        class MockLauncher:
            """Mock launcher that tracks concurrent executions."""

            async def launch_browser(
                self, url: str, browser_type: BrowserType, instance_id: int
            ) -> LaunchResult:
                nonlocal current_concurrent, max_concurrent

                async with lock:
                    current_concurrent += 1
                    if current_concurrent > max_concurrent:
                        max_concurrent = current_concurrent

                # Small sleep to allow other tasks to start
                await asyncio.sleep(0.01)

                async with lock:
                    current_concurrent -= 1

                return LaunchResult(
                    url=url,
                    browser_type=browser_type,
                    instance_id=instance_id,
                    success=True,
                    load_time_ms=10.0,
                )

        # Create config with the generated concurrency limit
        config = ExecutionConfig(concurrency_limit=concurrency_limit)
        launcher = MockLauncher()
        engine = ExecutionEngine(config=config, launcher=launcher)

        # Generate test URLs
        urls = [f"https://example{i}.com" for i in range(url_count)]

        # Execute
        await engine.execute(urls)

        # Assert: max concurrent never exceeds the configured limit
        assert max_concurrent <= concurrency_limit, (
            f"Max concurrent tasks ({max_concurrent}) exceeded "
            f"concurrency limit ({concurrency_limit}) with "
            f"{url_count} URLs ({url_count * 6} total tasks)"
        )

    asyncio.run(run_test())
