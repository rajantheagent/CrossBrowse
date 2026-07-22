"""Unit tests for the CSVReader component.

Validates: Requirements 1.1, 1.4, 1.5, 1.6
"""

import os
from unittest.mock import patch, mock_open

import pytest

from browser_automation.csv_reader import CSVReader


@pytest.fixture
def csv_reader():
    """Provide a CSVReader instance."""
    return CSVReader()


class TestCSVReaderEmptyFile:
    """Test that an empty CSV file raises ValueError."""

    def test_empty_csv_raises_value_error(self, csv_reader, tmp_path):
        """An empty CSV file (no header, no data) should raise ValueError."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("", encoding="utf-8")

        with pytest.raises(ValueError, match="no data rows"):
            csv_reader.read(str(csv_file))


class TestCSVReaderHeaderOnly:
    """Test that a CSV with only a header row raises ValueError."""

    def test_header_only_raises_value_error(self, csv_reader, tmp_path):
        """A CSV file with only a header row and no data rows should raise ValueError."""
        csv_file = tmp_path / "header_only.csv"
        csv_file.write_text("url\n", encoding="utf-8")

        with pytest.raises(ValueError, match="no data rows"):
            csv_reader.read(str(csv_file))


class TestCSVReaderSingleDataRow:
    """Test that a CSV with a single data row returns one URL."""

    def test_single_data_row_returns_one_url(self, csv_reader, tmp_path):
        """A CSV with header + one data row should return a list with one URL."""
        csv_file = tmp_path / "single.csv"
        csv_file.write_text("url\nhttps://example.com\n", encoding="utf-8")

        result = csv_reader.read(str(csv_file))

        assert result == ["https://example.com"]
        assert len(result) == 1


class TestCSVReaderMultipleColumns:
    """Test that CSVReader extracts only the first column."""

    def test_multiple_columns_extracts_first_only(self, csv_reader, tmp_path):
        """When CSV has multiple columns, only the first column values are returned."""
        csv_file = tmp_path / "multi_col.csv"
        content = "url,name,status\nhttps://example.com,Example,active\nhttps://test.org,Test,inactive\n"
        csv_file.write_text(content, encoding="utf-8")

        result = csv_reader.read(str(csv_file))

        assert result == ["https://example.com", "https://test.org"]
        assert len(result) == 2


class TestCSVReaderFileNotFound:
    """Test that FileNotFoundError is raised for a missing file path."""

    def test_missing_file_raises_file_not_found_error(self, csv_reader, tmp_path):
        """Reading a non-existent file should raise FileNotFoundError."""
        non_existent = str(tmp_path / "does_not_exist.csv")

        with pytest.raises(FileNotFoundError, match="not found"):
            csv_reader.read(non_existent)


class TestCSVReaderPermissionError:
    """Test that PermissionError is raised for unreadable files."""

    def test_unreadable_file_raises_permission_error(self, csv_reader, tmp_path):
        """A file that cannot be read due to permissions should raise PermissionError."""
        csv_file = tmp_path / "no_access.csv"
        csv_file.write_text("url\nhttps://example.com\n", encoding="utf-8")

        # Use mock to simulate PermissionError (Windows-compatible approach)
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            # Also need to patch os.path.exists to return True since the file exists
            with patch("os.path.exists", return_value=True):
                with pytest.raises(PermissionError, match="Permission denied"):
                    csv_reader.read(str(csv_file))
