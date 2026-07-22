"""Unit tests for CLI argument parsing.

Tests cover:
- --csv and --url are mutually exclusive (Requirement 1.1, 1.3)
- At least one of --csv or --url is required (Requirement 1.1, 1.3)
- --concurrency accepts valid integer values (Requirement 6.3)
- --concurrency validation rejects values outside 1-50 (Requirement 6.6)
"""

import pytest

from browser_automation.cli import parse_args, run


class TestMutualExclusivity:
    """Test that --csv and --url are mutually exclusive."""

    def test_csv_and_url_together_raises_system_exit(self):
        """Providing both --csv and --url should cause argparse to exit with error."""
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--csv", "urls.csv", "--url", "https://example.com"])
        assert exc_info.value.code == 2

    def test_csv_alone_is_valid(self):
        """Providing only --csv should parse successfully."""
        args = parse_args(["--csv", "urls.csv"])
        assert args.csv == "urls.csv"
        assert args.url is None

    def test_url_alone_is_valid(self):
        """Providing only --url should parse successfully."""
        args = parse_args(["--url", "https://example.com"])
        assert args.url == "https://example.com"
        assert args.csv is None


class TestRequiredInput:
    """Test that at least one of --csv or --url is required."""

    def test_neither_csv_nor_url_raises_system_exit(self):
        """Providing neither --csv nor --url should cause argparse to exit with error."""
        with pytest.raises(SystemExit) as exc_info:
            parse_args([])
        assert exc_info.value.code == 2

    def test_only_concurrency_without_input_raises_system_exit(self):
        """Providing only --concurrency without --csv or --url should exit with error."""
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--concurrency", "5"])
        assert exc_info.value.code == 2


class TestConcurrencyParsing:
    """Test --concurrency argument parsing."""

    def test_concurrency_accepts_integer_value(self):
        """--concurrency with a valid integer should parse correctly."""
        args = parse_args(["--url", "https://example.com", "--concurrency", "5"])
        assert args.concurrency == 5

    def test_concurrency_default_is_none(self):
        """Without --concurrency, the value should default to None (unlimited)."""
        args = parse_args(["--url", "https://example.com"])
        assert args.concurrency is None

    def test_concurrency_without_value_raises_system_exit(self):
        """--concurrency without a value should cause argparse to exit with error."""
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--url", "https://example.com", "--concurrency"])
        assert exc_info.value.code == 2

    def test_concurrency_non_integer_raises_system_exit(self):
        """--concurrency with a non-integer value should cause argparse to exit with error."""
        with pytest.raises(SystemExit) as exc_info:
            parse_args(["--url", "https://example.com", "--concurrency", "abc"])
        assert exc_info.value.code == 2

    def test_concurrency_accepts_boundary_value_1(self):
        """--concurrency=1 should parse as integer 1."""
        args = parse_args(["--url", "https://example.com", "--concurrency", "1"])
        assert args.concurrency == 1

    def test_concurrency_accepts_boundary_value_50(self):
        """--concurrency=50 should parse as integer 50."""
        args = parse_args(["--url", "https://example.com", "--concurrency", "50"])
        assert args.concurrency == 50


class TestConcurrencyValidation:
    """Test that concurrency values outside 1-50 are rejected by the run() function.

    The concurrency range validation (1-50) is enforced by ExecutionEngine,
    which is invoked during run(). Values outside this range raise ValueError
    which run() catches and returns exit code 1.
    """

    @pytest.mark.asyncio
    async def test_concurrency_zero_returns_error(self):
        """Concurrency of 0 should result in a ValueError from ExecutionEngine."""
        from unittest.mock import MagicMock
        import argparse

        args = argparse.Namespace(csv=None, url="https://example.com", concurrency=0)
        exit_code = await run(args)
        assert exit_code == 1

    @pytest.mark.asyncio
    async def test_concurrency_negative_returns_error(self):
        """Negative concurrency should result in a ValueError from ExecutionEngine."""
        import argparse

        args = argparse.Namespace(csv=None, url="https://example.com", concurrency=-1)
        exit_code = await run(args)
        assert exit_code == 1

    @pytest.mark.asyncio
    async def test_concurrency_51_returns_error(self):
        """Concurrency of 51 should result in a ValueError from ExecutionEngine."""
        import argparse

        args = argparse.Namespace(csv=None, url="https://example.com", concurrency=51)
        exit_code = await run(args)
        assert exit_code == 1

    @pytest.mark.asyncio
    async def test_concurrency_100_returns_error(self):
        """Concurrency of 100 should result in a ValueError from ExecutionEngine."""
        import argparse

        args = argparse.Namespace(csv=None, url="https://example.com", concurrency=100)
        exit_code = await run(args)
        assert exit_code == 1
