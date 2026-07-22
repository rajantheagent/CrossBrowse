"""Property-based test for deduplication preserving insertion order.

Feature: browser-automation-framework, Property 2: Deduplication preserves insertion order

Validates: Requirements 1.2, 2.7
"""

import string

from hypothesis import given, settings
from hypothesis import strategies as st

from browser_automation.url_validator import URLValidator


# Strategy: generate a list of unique valid domain names, then build URLs from them
def _valid_domain_strategy():
    """Generate a valid domain label (alphanumeric + hyphens, non-empty, no leading/trailing hyphen)."""
    return st.text(
        alphabet=string.ascii_lowercase + string.digits,
        min_size=1,
        max_size=10,
    )


def _valid_url_strategy():
    """Generate a valid URL of the form http://{label}.{tld}."""
    scheme = st.sampled_from(["http", "https"])
    domain_label = _valid_domain_strategy()
    tld = st.sampled_from(["com", "org", "net", "io", "dev"])
    return st.tuples(scheme, domain_label, tld).map(
        lambda parts: f"{parts[0]}://{parts[1]}.{parts[2]}"
    )


def _unique_url_list_strategy(min_size=1, max_size=10):
    """Generate a list of unique valid URLs."""
    return st.lists(
        _valid_url_strategy(),
        min_size=min_size,
        max_size=max_size,
        unique=True,
    )


@st.composite
def urls_with_duplicates_strategy(draw):
    """Generate a list of valid URLs with intentional duplicates.

    Strategy:
    1. Draw a base list of unique valid URLs (at least 2)
    2. For each URL in the base list, decide how many times it appears (1-3)
    3. Shuffle the resulting list to create a realistic input with duplicates scattered
    """
    base_urls = draw(_unique_url_list_strategy(min_size=2, max_size=8))

    # Create a list with duplicates by repeating some URLs
    urls_with_dupes = []
    for url in base_urls:
        # Each URL appears 1 to 3 times
        repeat_count = draw(st.integers(min_value=1, max_value=3))
        urls_with_dupes.extend([url] * repeat_count)

    # Shuffle the list to scatter duplicates (use hypothesis to draw a permutation)
    shuffled = draw(st.permutations(urls_with_dupes))
    return list(shuffled)


class TestDeduplicationPreservesInsertionOrder:
    """Property 2: Deduplication preserves insertion order.

    For any list of URL strings containing duplicates, the deduplication process
    SHALL return a list containing each unique URL exactly once, in the order of
    its first occurrence in the input.

    **Validates: Requirements 1.2, 2.7**
    """

    @given(urls_with_dupes=urls_with_duplicates_strategy())
    @settings(max_examples=100)
    def test_deduplication_preserves_first_occurrence_order(self, urls_with_dupes: list[str]):
        """Verify deduplication returns unique URLs in first-occurrence order.

        Feature: browser-automation-framework, Property 2: Deduplication preserves insertion order
        **Validates: Requirements 1.2, 2.7**
        """
        validator = URLValidator()
        result = validator.validate(urls_with_dupes)

        # Compute expected: unique URLs in first-occurrence order
        seen = set()
        expected_order = []
        for url in urls_with_dupes:
            trimmed = url.strip()
            if trimmed not in seen:
                seen.add(trimmed)
                expected_order.append(trimmed)

        # All generated URLs are valid, so valid_urls should contain exactly
        # the unique set in first-occurrence order
        assert result.valid_urls == expected_order, (
            f"Expected deduplication in first-occurrence order.\n"
            f"Input: {urls_with_dupes}\n"
            f"Expected: {expected_order}\n"
            f"Got: {result.valid_urls}"
        )

    @given(urls_with_dupes=urls_with_duplicates_strategy())
    @settings(max_examples=100)
    def test_deduplication_contains_each_unique_url_exactly_once(self, urls_with_dupes: list[str]):
        """Verify the output contains each unique URL exactly once.

        Feature: browser-automation-framework, Property 2: Deduplication preserves insertion order
        **Validates: Requirements 1.2, 2.7**
        """
        validator = URLValidator()
        result = validator.validate(urls_with_dupes)

        # Count occurrences in output — each URL should appear exactly once
        from collections import Counter

        url_counts = Counter(result.valid_urls)
        for url, count in url_counts.items():
            assert count == 1, (
                f"URL '{url}' appears {count} times in output, expected exactly once."
            )

        # The number of valid URLs should equal the number of unique URLs in input
        unique_input_urls = set(url.strip() for url in urls_with_dupes)
        assert len(result.valid_urls) == len(unique_input_urls), (
            f"Expected {len(unique_input_urls)} unique URLs, got {len(result.valid_urls)}"
        )
