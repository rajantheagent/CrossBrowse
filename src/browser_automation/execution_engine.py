"""Execution engine for orchestrating parallel browser launches with concurrency control."""

import asyncio
import logging

from browser_automation.browser_launcher import BrowserLauncher
from browser_automation.models import BrowserType, ExecutionConfig, ExecutionSummary, LaunchResult

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """Orchestrates parallel browser launches with concurrency control.

    Generates a task matrix of (url, browser_type, instance_id) tuples and
    executes them concurrently using asyncio with an optional semaphore-based
    concurrency limit.
    """

    def __init__(self, config: ExecutionConfig, launcher: BrowserLauncher) -> None:
        """Initialize the execution engine.

        Args:
            config: Execution configuration including concurrency limit and browsers per URL.
            launcher: Browser launcher instance for executing individual browser tasks.

        Raises:
            ValueError: If concurrency_limit is outside the valid range [1, 50].
        """
        self._validate_concurrency_limit(config.concurrency_limit)
        self.config = config
        self.launcher = launcher

    def _validate_concurrency_limit(self, limit: int | None) -> None:
        """Validate that concurrency_limit is between 1 and 50 if provided.

        Args:
            limit: The concurrency limit to validate. None means unlimited.

        Raises:
            ValueError: If limit is provided and not in range [1, 50].
        """
        if limit is None:
            return
        if limit < 1 or limit > 50:
            raise ValueError(
                f"Concurrency limit must be between 1 and 50, got {limit}"
            )

    def _generate_task_matrix(
        self, urls: list[str]
    ) -> list[tuple[str, BrowserType, int]]:
        """Generate the task matrix for all URLs.

        For each URL, creates tasks based on the browsers_per_url configuration.
        With default config (2 per browser type), this produces 6 tasks per URL:
        (url, CHROMIUM, 0), (url, CHROMIUM, 1), (url, EDGE, 0), (url, EDGE, 1),
        (url, FIREFOX, 0), (url, FIREFOX, 1).

        Args:
            urls: List of validated URLs to generate tasks for.

        Returns:
            List of (url, browser_type, instance_id) tuples representing all tasks.
        """
        tasks: list[tuple[str, BrowserType, int]] = []
        for url in urls:
            for browser_type, count in self.config.browsers_per_url.items():
                for instance_id in range(count):
                    tasks.append((url, browser_type, instance_id))
        return tasks

    async def execute(self, urls: list[str]) -> ExecutionSummary:
        """Execute browser launches for all URLs in parallel.

        Generates the task matrix and executes all tasks concurrently,
        using asyncio.Semaphore for concurrency limiting if configured.

        Args:
            urls: List of validated URLs to execute against.

        Returns:
            ExecutionSummary with results for all tasks.
        """
        task_matrix = self._generate_task_matrix(urls)

        # Create semaphore if concurrency limit is configured
        semaphore: asyncio.Semaphore | None = None
        if self.config.concurrency_limit is not None:
            semaphore = asyncio.Semaphore(self.config.concurrency_limit)

        async def _run_task(
            url: str, browser_type: BrowserType, instance_id: int
        ) -> LaunchResult:
            """Worker that launches a single browser task with optional semaphore control."""
            try:
                if semaphore is not None:
                    async with semaphore:
                        return await self.launcher.launch_browser(
                            url, browser_type, instance_id
                        )
                else:
                    return await self.launcher.launch_browser(
                        url, browser_type, instance_id
                    )
            except Exception as exc:
                error_msg = (
                    f"Task failed for {browser_type.value} instance {instance_id} "
                    f"navigating to {url}: {exc}"
                )
                logger.error(error_msg)
                return LaunchResult(
                    url=url,
                    browser_type=browser_type,
                    instance_id=instance_id,
                    success=False,
                    error_message=error_msg,
                )

        # Launch all tasks concurrently
        coroutines = [
            _run_task(url, browser_type, instance_id)
            for url, browser_type, instance_id in task_matrix
        ]
        results: list[LaunchResult] = await asyncio.gather(*coroutines)

        # Aggregate results into ExecutionSummary
        successful = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)

        return ExecutionSummary(
            total_tasks=len(results),
            successful=successful,
            failed=failed,
            results=list(results),
        )
