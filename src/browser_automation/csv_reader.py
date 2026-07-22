"""CSV Reader component for the Browser Automation Framework."""

import csv
import logging
import os

logger = logging.getLogger(__name__)


class CSVReader:
    """Reads and parses URL data from CSV files."""

    def read(self, file_path: str) -> list[str]:
        """
        Read URLs from the first column of a CSV file.

        The first row is always treated as a header and skipped.
        Empty rows are skipped. Only the first column value is extracted.

        Args:
            file_path: Path to the CSV file to read.

        Returns:
            A list of URL strings from the first column of each data row.

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read due to permissions.
            IOError: If the file cannot be read for other I/O reasons.
            ValueError: If no data rows are found after reading.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        try:
            with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)

                # Skip header row
                try:
                    next(reader)
                except StopIteration:
                    # File is empty - no header, no data
                    raise ValueError(
                        f"CSV file contains no data rows: {file_path}"
                    )

                urls: list[str] = []
                for row in reader:
                    # Skip empty rows
                    if not row or not row[0].strip():
                        continue
                    urls.append(row[0])

                if not urls:
                    raise ValueError(
                        f"CSV file contains no data rows: {file_path}"
                    )

                logger.info(
                    "Read %d URL(s) from CSV file: %s", len(urls), file_path
                )
                return urls

        except PermissionError:
            raise PermissionError(
                f"Permission denied reading CSV file: {file_path}"
            )
        except IOError as e:
            raise IOError(
                f"Error reading CSV file: {file_path} - {e}"
            )
