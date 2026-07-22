"""Property-based tests for ExecutionEngine task matrix generation.

Feature: browser-automation-framework, Property 8: Task matrix invariant
"""

from collections import Counter
from unittest.mock import MagicMock

from hypothesis import given, settings
from hypothesis import strategies as st

from browser_automation.execution_engine import ExecutionEngine
from browser_automation.models import BrowserType, ExecutionConfig


# Strategy: generate a valid URL label (alphanumeric, lowercase, 1-20 chars)
url_label_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Nd")),
    min_size=1,
    max_size=20,
).filter(lambda s: len(s) > 0 and s[0].isalpha())


# Strategy: generate a list of 1-10 unique valid URLs
url_list_strategy = st.lists(
    url_label_strategy.map(lambda label: f"http://{label}.com"),
    min_size=1,
    max_size=10,
    unique=True,
)


@settings(max_examples=100)
@given(urls=url_list_strategy)
def test_task_matrix_invariant(urls: list[str]):
    """Property 8: Task matrix invariant

    For any list of N valid URLs (N >= 1), the Execution_Engine SHALL generate
    a task matrix containing exactly N x 6 entries, with each URL assigned
    exactly 2 chromium tasks, 2 edge tasks, and 2 firefox tasks.

    **Validates: Requirements 4.4, 7.1, 7.2**
    """
    # Arrange: create ExecutionEngine with default config and a mock launcher
    config = ExecutionConfig()
    mock_launcher = MagicMock()
    engine = ExecutionEngine(config=config, launcher=mock_launcher)

    n = len(urls)

    # Act: generate the task matrix
    task_matrix = engine._generate_task_matrix(urls)

    # Assert 1: total entries == N x 6
    assert len(task_matrix) == n * 6, (
        f"Expected {n * 6} entries for {n} URLs, got {len(task_matrix)}"
    )

    # Assert 2: each URL has exactly 2 CHROMIUM, 2 EDGE, 2 FIREFOX tasks
    for url in urls:
        url_tasks = [(u, bt, iid) for u, bt, iid in task_matrix if u == url]
        assert len(url_tasks) == 6, (
            f"Expected 6 tasks for URL '{url}', got {len(url_tasks)}"
        )

        browser_counts = Counter(bt for _, bt, _ in url_tasks)
        assert browser_counts[BrowserType.CHROMIUM] == 2, (
            f"Expected 2 CHROMIUM tasks for '{url}', "
            f"got {browser_counts[BrowserType.CHROMIUM]}"
        )
        assert browser_counts[BrowserType.EDGE] == 2, (
            f"Expected 2 EDGE tasks for '{url}', "
            f"got {browser_counts[BrowserType.EDGE]}"
        )
        assert browser_counts[BrowserType.FIREFOX] == 2, (
            f"Expected 2 FIREFOX tasks for '{url}', "
            f"got {browser_counts[BrowserType.FIREFOX]}"
        )

    # Assert 3: instance_ids are 0 and 1 for each browser type per URL
    for url in urls:
        for browser_type in BrowserType:
            instance_ids = sorted(
                iid
                for u, bt, iid in task_matrix
                if u == url and bt == browser_type
            )
            assert instance_ids == [0, 1], (
                f"Expected instance_ids [0, 1] for '{url}' / "
                f"{browser_type.value}, got {instance_ids}"
            )
