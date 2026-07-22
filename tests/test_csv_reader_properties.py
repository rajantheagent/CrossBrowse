"""Property-based tests for CSVReader component.

Feature: browser-automation-framework, Property 1: CSV first-column extraction
"""

import csv
import os
import tempfile

from hypothesis import given, settings
from hypothesis import strategies as st

from browser_automation.csv_reader import CSVReader


# Strategy: generate non-empty cell values without commas or newlines
cell_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "S"),
        blacklist_characters=",\n\r",
    ),
    min_size=1,
    max_size=50,
).filter(lambda s: s.strip() != "")


@settings(max_examples=100)
@given(
    num_rows=st.integers(min_value=1, max_value=20),
    num_cols=st.integers(min_value=1, max_value=5),
    data=st.data(),
)
def test_csv_first_column_extraction(num_rows, num_cols, data):
    """Property 1: CSV first-column extraction

    For any CSV file with N data rows (excluding header) and M columns,
    CSVReader SHALL return exactly N strings, each being the value from
    the first column of the corresponding row.

    **Validates: Requirements 1.1**
    """
    # Generate the CSV data matrix: num_rows x num_cols
    rows = []
    for _ in range(num_rows):
        row = [data.draw(cell_strategy) for _ in range(num_cols)]
        rows.append(row)

    # Generate header row
    header = [f"col_{i}" for i in range(num_cols)]

    # Write CSV to a temporary file
    tmp_file = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline="", encoding="utf-8"
    )
    try:
        writer = csv.writer(tmp_file)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)
        tmp_file.close()

        # Act: read the CSV using CSVReader
        reader = CSVReader()
        result = reader.read(tmp_file.name)

        # Assert: returns exactly N strings
        assert len(result) == num_rows, (
            f"Expected {num_rows} rows, got {len(result)}"
        )

        # Assert: each string matches the first column value
        expected_first_col = [row[0] for row in rows]
        assert result == expected_first_col, (
            f"First column mismatch.\n"
            f"Expected: {expected_first_col}\n"
            f"Got: {result}"
        )
    finally:
        os.unlink(tmp_file.name)
