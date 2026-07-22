"""Browser launcher with isolated context management using Playwright."""

import asyncio
import logging
import time

from browser_automation.models import BrowserType, LaunchResult

logger = logging.getLogger(__name__)

# Supported browser type string values
SUPPORTED_BROWSER_TYPES = [bt.value for bt in BrowserType]


def validate_browser_type(browser_type_str: str) -> BrowserType:
    """Validate a browser type string and return the corresponding BrowserType enum.

    Args:
        browser_type_str: A string representing the desired browser type.

    Returns:
        The matching BrowserType enum value.

    Raises:
        ValueError: If the browser type string is not one of the supported types.
            The error message includes all supported browser type names.
    """
    try:
        return BrowserType(browser_type_str)
    except ValueError:
        supported = ", ".join(SUPPORTED_BROWSER_TYPES)
        raise ValueError(
            f"Invalid browser type '{browser_type_str}'. "
            f"Supported types are: {supported}"
        )


class BrowserLauncher:
    """Launches browser instances in isolated contexts and navigates to URLs."""

    LAUNCH_TIMEOUT_MS: int = 30_000
    NAVIGATION_TIMEOUT_MS: int = 60_000
    CONTEXT_CLOSE_TIMEOUT_MS: int = 5_000

    def __init__(self, headless: bool = False) -> None:
        """Initialize the browser launcher.

        Args:
            headless: If True, browsers run without visible windows.
                      If False (default), browsers are visible on screen.
        """
        self.headless = headless

    async def launch_browser(
        self,
        url: str,
        browser_type: BrowserType,
        instance_id: int,
    ) -> LaunchResult:
        """
        Launch a single browser instance in an isolated context and navigate to the URL.

        Creates a new BrowserContext (isolated cookies, cache, storage, session),
        creates a new Page within that context, navigates to the URL waiting for
        'domcontentloaded', and closes the context on completion.

        Args:
            url: The target URL to navigate to.
            browser_type: The browser type to launch.
            instance_id: The instance identifier for this launch.

        Returns:
            LaunchResult with success/failure status, error message, and load time.
        """
        from playwright.async_api import (
            async_playwright,
            TimeoutError as PlaywrightTimeoutError,
        )

        context = None
        browser = None

        try:
            async with async_playwright() as pw:
                # Map BrowserType to Playwright browser type and launch
                pw_browser_type = self._get_playwright_browser_type(pw, browser_type)

                launch_kwargs: dict = {"timeout": self.LAUNCH_TIMEOUT_MS, "headless": self.headless}
                if browser_type == BrowserType.EDGE:
                    launch_kwargs["channel"] = "msedge"

                try:
                    browser = await pw_browser_type.launch(**launch_kwargs)
                except (PlaywrightTimeoutError, Exception) as exc:
                    error_msg = (
                        f"Browser launch failed for {browser_type.value} "
                        f"instance {instance_id} navigating to {url}: {exc}"
                    )
                    logger.error(error_msg)
                    return LaunchResult(
                        url=url,
                        browser_type=browser_type,
                        instance_id=instance_id,
                        success=False,
                        error_message=error_msg,
                    )

                try:
                    # Create a new isolated BrowserContext
                    context = await browser.new_context()

                    # Create a new page and navigate
                    page = await context.new_page()

                    start_time = time.perf_counter()
                    await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=self.NAVIGATION_TIMEOUT_MS,
                    )
                    end_time = time.perf_counter()
                    load_time_ms = (end_time - start_time) * 1000

                    # Keep browser open for viewing in headed mode
                    if not self.headless:
                        await asyncio.sleep(30)

                    return LaunchResult(
                        url=url,
                        browser_type=browser_type,
                        instance_id=instance_id,
                        success=True,
                        load_time_ms=load_time_ms,
                    )

                except PlaywrightTimeoutError as exc:
                    error_msg = (
                        f"Navigation timeout for {browser_type.value} "
                        f"instance {instance_id} navigating to {url}: {exc}"
                    )
                    logger.error(error_msg)
                    return LaunchResult(
                        url=url,
                        browser_type=browser_type,
                        instance_id=instance_id,
                        success=False,
                        error_message=error_msg,
                    )

                except Exception as exc:
                    error_msg = (
                        f"Context/navigation failure for {browser_type.value} "
                        f"instance {instance_id} navigating to {url}: {exc}"
                    )
                    logger.error(error_msg)
                    return LaunchResult(
                        url=url,
                        browser_type=browser_type,
                        instance_id=instance_id,
                        success=False,
                        error_message=error_msg,
                    )

                finally:
                    # Close and dispose of the BrowserContext within 5 seconds
                    if context:
                        try:
                            await asyncio.wait_for(
                                context.close(),
                                timeout=self.CONTEXT_CLOSE_TIMEOUT_MS / 1000,
                            )
                        except (asyncio.TimeoutError, Exception):
                            logger.error(
                                "Failed to close context within %dms for %s instance %d",
                                self.CONTEXT_CLOSE_TIMEOUT_MS,
                                browser_type.value,
                                instance_id,
                            )
                    # Close the browser
                    if browser:
                        try:
                            await browser.close()
                        except Exception:
                            pass

        except Exception as exc:
            error_msg = (
                f"Unexpected failure for {browser_type.value} "
                f"instance {instance_id} navigating to {url}: {exc}"
            )
            logger.error(error_msg)
            return LaunchResult(
                url=url,
                browser_type=browser_type,
                instance_id=instance_id,
                success=False,
                error_message=error_msg,
            )

    def _get_playwright_browser_type(self, pw, browser_type: BrowserType):
        """Map BrowserType enum to Playwright's browser type object.

        Both CHROMIUM and EDGE map to Playwright's chromium type.
        FIREFOX maps to Playwright's firefox type.
        """
        if browser_type in (BrowserType.CHROMIUM, BrowserType.EDGE):
            return pw.chromium
        elif browser_type == BrowserType.FIREFOX:
            return pw.firefox
        else:
            raise ValueError(
                f"Unsupported browser type: {browser_type}. "
                f"Supported types: chromium, edge, firefox"
            )
