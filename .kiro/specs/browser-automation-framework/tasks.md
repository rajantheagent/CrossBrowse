# Implementation Plan: Browser Automation Framework

## Overview

This plan implements a production-ready Python browser automation framework using Playwright, asyncio, and CSV-based URL configuration. The implementation follows the pipeline architecture: Input Layer (CSV parsing, URL validation) → Orchestration Layer (asyncio concurrency control) → Execution Layer (Playwright browser lifecycle). Each task builds incrementally, with testing integrated alongside implementation.

## Tasks

- [x] 1. Set up project structure and core data models
  - [x] 1.1 Create project directory structure and install dependencies
    - Create `src/browser_automation/` package directory with `__init__.py`
    - Create `tests/` directory with `__init__.py` and `conftest.py`
    - Create `pyproject.toml` with dependencies: playwright, pytest, hypothesis, pytest-asyncio
    - Run `pip install -e .` and `playwright install` to set up the environment
    - _Requirements: 3.1, 3.2, 3.3, 6.1_

  - [x] 1.2 Define core data models and enums
    - Create `src/browser_automation/models.py`
    - Implement `BrowserType` enum with values: CHROMIUM, EDGE, FIREFOX
    - Implement `ValidationResult` frozen dataclass with `valid_urls: list[str]` and `invalid_entries: list[tuple[str, str]]`
    - Implement `LaunchResult` frozen dataclass with fields: url, browser_type, instance_id, success, error_message, load_time_ms
    - Implement `ExecutionConfig` frozen dataclass with concurrency_limit and browsers_per_url fields
    - Implement `ExecutionSummary` frozen dataclass with total_tasks, successful, failed, results fields
    - _Requirements: 3.4, 4.4, 6.3_

- [x] 2. Implement CSV Reader component
  - [x] 2.1 Implement CSVReader class
    - Create `src/browser_automation/csv_reader.py`
    - Implement `CSVReader.read(file_path: str) -> list[str]` method
    - Read URLs from the first column of each row, skipping the header row
    - Raise `FileNotFoundError` with file path if the file does not exist
    - Raise `PermissionError` or `IOError` if the file cannot be read
    - Raise `ValueError` if no data rows are found after reading
    - _Requirements: 1.1, 1.4, 1.5, 1.6_

  - [x] 2.2 Write property test for CSV first-column extraction
    - **Property 1: CSV first-column extraction**
    - Use Hypothesis to generate random CSV data with N rows and M columns
    - Verify that CSVReader returns exactly N strings, each being the first-column value
    - **Validates: Requirements 1.1**

  - [x] 2.3 Write unit tests for CSVReader
    - Test empty CSV file raises ValueError
    - Test CSV with header only raises ValueError
    - Test CSV with single data row returns one URL
    - Test CSV with multiple columns extracts only first column
    - Test FileNotFoundError for missing file path
    - Test PermissionError for unreadable file
    - _Requirements: 1.1, 1.4, 1.5, 1.6_

- [x] 3. Implement URL Validator component
  - [x] 3.1 Implement URLValidator class
    - Create `src/browser_automation/url_validator.py`
    - Implement `URLValidator.validate(urls: list[str]) -> ValidationResult` method
    - Trim leading/trailing whitespace from each URL
    - Validate scheme is exactly "http" or "https"
    - Validate hostname contains only alphanumeric characters, hyphens, and dots, with at least one dot separating a non-empty domain and TLD
    - Accept optional port, path, query parameters, and fragment identifiers
    - Deduplicate URLs preserving insertion order of first occurrence
    - Log invalid URLs with the reason for failure using Python logging module
    - Implement `URLValidator.is_valid_url(url: str) -> tuple[bool, str]` helper method
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [x] 3.2 Write property tests for URL validation
    - **Property 3: Whitespace trimming invariant** — generate valid URLs with random padding, verify `validate(ws + u + ws)` equals `validate(u)`
    - **Property 4: URL scheme validation** — generate URLs with random schemes, verify only http/https accepted
    - **Property 5: URL hostname validation** — generate random hostnames, verify character and dot rules
    - **Property 6: Validation correctly partitions URLs** — generate mixed URLs, verify union of valid+invalid equals deduplicated input
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

  - [x] 3.3 Write property test for deduplication
    - **Property 2: Deduplication preserves insertion order**
    - Use Hypothesis to generate lists with duplicate URLs
    - Verify the returned list contains each unique URL exactly once in first-occurrence order
    - **Validates: Requirements 1.2, 2.7**

  - [x] 3.4 Write unit tests for URLValidator
    - Test URL with missing scheme is rejected
    - Test URL with "ftp" scheme is rejected
    - Test URL with invalid hostname characters is rejected
    - Test URL with no dot in hostname is rejected
    - Test valid URL with port, path, query, and fragment is accepted
    - Test empty string is rejected
    - Test whitespace-only string is rejected
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Checkpoint - Validate input layer
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement Browser Launcher component
  - [x] 5.1 Implement BrowserLauncher class
    - Create `src/browser_automation/browser_launcher.py`
    - Implement `BrowserLauncher.launch_browser(url, browser_type, instance_id) -> LaunchResult` async method
    - Map BrowserType.CHROMIUM and BrowserType.EDGE to Playwright's chromium browser type, BrowserType.FIREFOX to firefox
    - For Edge, use chromium with channel="msedge"
    - Create a new isolated BrowserContext for each launch (separate cookies, cache, local storage, session)
    - Create a new Page within the context and navigate to the URL
    - Wait for "domcontentloaded" event with 60-second navigation timeout
    - Close and dispose of the BrowserContext within 5 seconds of completion
    - Return LaunchResult with success/failure status, error message, and load time
    - Handle launch timeout (30s), navigation timeout (60s), and context creation failures gracefully
    - Log errors at ERROR level with browser type, URL, and reason
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.5, 4.6, 4.7, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

  - [x] 5.2 Implement browser type validation
    - Implement validation that raises ValueError for invalid browser types
    - Error message must include all supported types: "chromium", "edge", "firefox"
    - _Requirements: 3.6_

  - [x] 5.3 Write property test for invalid browser type
    - **Property 7: Invalid browser type produces error**
    - Use Hypothesis to generate random strings not in {"chromium", "edge", "firefox"}
    - Verify the error message contains all three supported browser type names
    - **Validates: Requirements 3.6**

  - [x] 5.4 Write unit tests for BrowserLauncher
    - Test that invalid browser type returns descriptive error with supported types listed
    - Test that LaunchResult captures success with load_time_ms
    - Test that LaunchResult captures failure with error_message
    - _Requirements: 3.4, 3.5, 3.6_

- [x] 6. Implement Execution Engine component
  - [x] 6.1 Implement ExecutionEngine class with task matrix generation
    - Create `src/browser_automation/execution_engine.py`
    - Implement `ExecutionEngine.__init__(config, launcher)` accepting ExecutionConfig and BrowserLauncher
    - Implement `_validate_concurrency_limit(limit)` that raises ValueError if limit < 1 or > 50
    - Implement task matrix generation: for each URL, create 2 chromium + 2 edge + 2 firefox tasks (6 per URL)
    - _Requirements: 4.4, 6.6, 7.1, 7.2_

  - [x] 6.2 Implement parallel execution with concurrency control
    - Implement `ExecutionEngine.execute(urls: list[str]) -> ExecutionSummary` async method
    - Use `asyncio.Semaphore` to enforce the configured concurrency limit
    - If no concurrency limit configured, run all tasks concurrently without restriction
    - Catch and log failures for individual tasks without halting execution of remaining tasks
    - Aggregate all LaunchResults into ExecutionSummary with total, successful, and failed counts
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.3, 7.4_

  - [x] 6.3 Write property test for task matrix invariant
    - **Property 8: Task matrix invariant**
    - Use Hypothesis to generate lists of 1-10 valid URLs
    - Verify the task matrix contains exactly N × 6 entries with correct browser distribution
    - **Validates: Requirements 4.4, 7.1, 7.2**

  - [x] 6.4 Write property test for concurrency limit enforcement
    - **Property 9: Concurrency limit enforcement**
    - Use Hypothesis to generate concurrency limits between 1-50 and task counts
    - Use an asyncio counter to track max simultaneous tasks during execution
    - Verify the max concurrent count never exceeds the configured limit
    - **Validates: Requirements 6.3, 7.3**

  - [x] 6.5 Write property test for failure isolation
    - **Property 10: Failure isolation**
    - Use Hypothesis to generate random failure patterns across tasks
    - Verify all non-failing tasks complete and ExecutionSummary contains results for every task
    - **Validates: Requirements 6.5, 7.4**

  - [x] 6.6 Write property test for invalid concurrency limit rejection
    - **Property 11: Invalid concurrency limit rejection**
    - Use Hypothesis to generate integers outside range [1, 50]
    - Verify ValueError is raised with a message indicating valid range
    - **Validates: Requirements 6.6**

  - [x] 6.7 Write unit tests for ExecutionEngine
    - Test concurrency limit of 0 raises ValueError
    - Test concurrency limit of 51 raises ValueError
    - Test concurrency limit of 1 is accepted
    - Test concurrency limit of 50 is accepted
    - Test None concurrency limit means unlimited
    - Test single URL generates exactly 6 tasks
    - Test multiple URLs generate N × 6 tasks
    - _Requirements: 6.3, 6.4, 6.6, 7.1, 7.2_

- [x] 7. Checkpoint - Validate orchestration and execution layers
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement CLI entry point and wire components together
  - [x] 8.1 Implement CLI entry point
    - Create `src/browser_automation/cli.py`
    - Use `argparse` to parse command-line arguments: `--csv <path>`, `--url <url>`, `--concurrency <n>`
    - Validate that either `--csv` or `--url` is provided (mutually exclusive but one required)
    - Wire CSVReader → URLValidator → ExecutionEngine → BrowserLauncher pipeline
    - Implement the `main()` function as the async entry point using `asyncio.run()`
    - Handle fatal errors (FileNotFoundError, ValueError) by printing user-friendly messages and exiting with non-zero code
    - Print execution summary (total, successful, failed) on completion
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 6.1_

  - [x] 8.2 Implement single URL input path
    - Handle `--url` argument by bypassing CSVReader and passing the single URL directly to URLValidator
    - Validate the single URL follows the same validation rules as CSV-sourced URLs
    - _Requirements: 1.3_

  - [x] 8.3 Configure logging
    - Set up Python `logging` module with structured log messages
    - Configure ERROR level for fatal and individual task failures
    - Configure WARNING level for skipped items (invalid URLs, failed browser instances)
    - Configure INFO level for normal execution flow
    - Configure DEBUG level for detailed state (semaphore acquisition, context lifecycle)
    - _Requirements: 2.5, 3.5, 4.5, 4.7, 5.6, 6.5_

  - [x] 8.4 Write unit tests for CLI argument parsing
    - Test `--csv` and `--url` are mutually exclusive
    - Test at least one of `--csv` or `--url` is required
    - Test `--concurrency` accepts values 1-50
    - Test `--concurrency` rejects values outside 1-50
    - _Requirements: 1.1, 1.3, 6.3, 6.6_

- [x] 9. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation after each major layer
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- The implementation uses Python with Playwright, asyncio, and Hypothesis as specified in the design
- All browser instances use isolated BrowserContexts for session separation
- The concurrency control uses asyncio.Semaphore for limiting parallel execution

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["2.1", "3.1"] },
    { "id": 3, "tasks": ["2.2", "2.3", "3.2", "3.3", "3.4"] },
    { "id": 4, "tasks": ["5.1", "5.2", "6.1"] },
    { "id": 5, "tasks": ["5.3", "5.4", "6.2"] },
    { "id": 6, "tasks": ["6.3", "6.4", "6.5", "6.6", "6.7"] },
    { "id": 7, "tasks": ["8.1", "8.2", "8.3"] },
    { "id": 8, "tasks": ["8.4"] }
  ]
}
```
