"""CLI entry point for the Browser Automation Framework."""

import argparse
import asyncio
import logging
import sys

from browser_automation.browser_launcher import BrowserLauncher
from browser_automation.csv_reader import CSVReader
from browser_automation.execution_engine import ExecutionEngine
from browser_automation.models import ExecutionConfig
from browser_automation.url_validator import URLValidator

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        argv: Argument list to parse. Defaults to sys.argv[1:] if None.

    Returns:
        Parsed arguments namespace with csv, url, and concurrency attributes.
    """
    parser = argparse.ArgumentParser(
        description="Browser Automation Framework - Cross-browser testing with Playwright and asyncio."
    )

    # Mutually exclusive group: --csv or --url (one required)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--csv",
        type=str,
        help="Path to CSV file containing URLs to test",
    )
    input_group.add_argument(
        "--url",
        type=str,
        help="Single URL to test",
    )

    parser.add_argument(
        "--concurrency",
        type=int,
        default=None,
        help="Maximum number of simultaneous browser instances (1-50)",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run browsers in headless mode (no visible window). Default: visible.",
    )

    return parser.parse_args(argv)


async def run(args: argparse.Namespace) -> int:
    """Execute the browser automation pipeline.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for failure).
    """
    try:
        # Determine URL source: --url bypasses CSVReader entirely
        if args.url:
            # Single URL input path: bypass CSVReader, pass directly to URLValidator
            raw_urls = [args.url]
        else:
            # CSV input path: read URLs from CSV file
            csv_reader = CSVReader()
            raw_urls = csv_reader.read(args.csv)

        # Validate URLs (same validation rules regardless of input source)
        validator = URLValidator()
        validation_result = validator.validate(raw_urls)

        if not validation_result.valid_urls:
            print("Error: No valid URLs found after validation.", file=sys.stderr)
            return 1

        # Log invalid entries
        for url, reason in validation_result.invalid_entries:
            logger.warning("Skipped invalid URL '%s': %s", url, reason)

        # Configure execution
        config = ExecutionConfig(concurrency_limit=args.concurrency)

        # Create launcher and engine
        launcher = BrowserLauncher(headless=args.headless)
        engine = ExecutionEngine(config=config, launcher=launcher)

        # Execute browser launches
        summary = await engine.execute(validation_result.valid_urls)

        # Print execution summary
        print(f"\nExecution Summary:")
        print(f"  Total tasks: {summary.total_tasks}")
        print(f"  Successful:  {summary.successful}")
        print(f"  Failed:      {summary.failed}")

        return 0 if summary.failed == 0 else 1

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def configure_logging() -> None:
    """Configure logging with structured log messages.

    Sets up the Python logging module with:
    - ERROR level for fatal and individual task failures
    - WARNING level for skipped items (invalid URLs, failed browser instances)
    - INFO level for normal execution flow
    - DEBUG level for detailed state (semaphore acquisition, context lifecycle)
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main(argv: list[str] | None = None) -> None:
    """Main entry point for the CLI.

    Args:
        argv: Optional argument list for testing. Defaults to sys.argv[1:] if None.
    """
    args = parse_args(argv)
    configure_logging()
    exit_code = asyncio.run(run(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
