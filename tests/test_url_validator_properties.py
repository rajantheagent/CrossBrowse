"""Property-based tests for URLValidator.

Feature: browser-automation-framework
Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
"""

import string

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

from browser_automation.url_validator import URLValidator


# --- Strategies ---

# Valid TLDs for generating realistic hostnames
VALID_TLDS = ["com", "org", "net", "io", "dev", "co", "uk", "us", "info"]

# Whitespace characters for padding
WHITESPACE_CHARS = " \t\n\r\x0b\x0c"


def valid_hostname_label():
    """Generate a valid hostname label: alphanumeric + hyphens, non-empty, no leading/trailing hyphen."""
    return st.from_regex(r"[a-z][a-z0-9\-]{0,10}[a-z0-9]", fullmatch=True).filter(
        lambda s: len(s) >= 1
    )


def valid_hostname():
    """Generate a valid hostname with at least one dot separating non-empty labels."""
    return st.tuples(
        valid_hostname_label(),
        st.sampled_from(VALID_TLDS),
    ).map(lambda t: f"{t[0]}.{t[1]}")


def valid_url():
    """Generate a valid URL with http or https scheme and valid hostname."""
    return st.tuples(
        st.sampled_from(["http", "https"]),
        valid_hostname(),
    ).map(lambda t: f"{t[0]}://{t[1]}")


def whitespace_padding():
    """Generate random whitespace padding (spaces, tabs, newlines)."""
    return st.text(
        alphabet=WHITESPACE_CHARS,
        min_size=0,
        max_size=5,
    )


# --- Property Tests ---


class TestProperty3WhitespaceTrimming:
    """Property 3: Whitespace trimming invariant

    Feature: browser-automation-framework, Property 3: Whitespace trimming invariant

    For any valid URL string u, and any combination of leading/trailing
    whitespace characters ws, validate(ws + u + ws) SHALL produce the
    same result as validate(u).

    **Validates: Requirements 2.1**
    """

    @given(
        url=valid_url(),
        leading_ws=whitespace_padding(),
        trailing_ws=whitespace_padding(),
    )
    @settings(max_examples=100)
    def test_whitespace_trimming_invariant(self, url, leading_ws, trailing_ws):
        """Validates: Requirements 2.1"""
        validator = URLValidator()

        # Validate the URL without padding
        result_clean = validator.validate([url])

        # Validate the URL with padding
        padded_url = leading_ws + url + trailing_ws
        result_padded = validator.validate([padded_url])

        # Both should produce the same valid URLs
        assert result_clean.valid_urls == result_padded.valid_urls
        # Both should have no invalid entries (since the URL is valid)
        assert len(result_clean.invalid_entries) == 0
        assert len(result_padded.invalid_entries) == 0


class TestProperty4SchemeValidation:
    """Property 4: URL scheme validation

    Feature: browser-automation-framework, Property 4: URL scheme validation

    For any URL string, the URL_Validator SHALL accept it only if its
    scheme component is exactly "http" or "https". For any URL with a
    scheme other than these, the validator SHALL reject it.

    **Validates: Requirements 2.2**
    """

    @given(
        scheme=st.sampled_from(["http", "https"]),
        hostname=valid_hostname(),
    )
    @settings(max_examples=100)
    def test_valid_schemes_accepted(self, scheme, hostname):
        """Validates: Requirements 2.2"""
        validator = URLValidator()
        url = f"{scheme}://{hostname}"

        result = validator.validate([url])

        assert url in result.valid_urls
        assert len(result.invalid_entries) == 0

    @given(
        scheme=st.text(
            alphabet=string.ascii_lowercase + string.digits,
            min_size=1,
            max_size=10,
        ).filter(lambda s: s not in ("http", "https")),
        hostname=valid_hostname(),
    )
    @settings(max_examples=100)
    def test_invalid_schemes_rejected(self, scheme, hostname):
        """Validates: Requirements 2.2"""
        validator = URLValidator()
        url = f"{scheme}://{hostname}"

        result = validator.validate([url])

        assert len(result.valid_urls) == 0
        assert len(result.invalid_entries) == 1
        assert result.invalid_entries[0][0] == url
        # The reason should mention the scheme issue
        assert "scheme" in result.invalid_entries[0][1].lower() or "http" in result.invalid_entries[0][1].lower()


class TestProperty5HostnameValidation:
    """Property 5: URL hostname validation

    Feature: browser-automation-framework, Property 5: URL hostname validation

    For any string used as a hostname, the URL_Validator SHALL accept it
    only if it contains exclusively alphanumeric characters, hyphens, and
    dots, AND contains at least one dot separating a non-empty domain
    label from a non-empty top-level domain label.

    **Validates: Requirements 2.3**
    """

    @given(hostname=valid_hostname())
    @settings(max_examples=100)
    def test_valid_hostnames_accepted(self, hostname):
        """Validates: Requirements 2.3"""
        validator = URLValidator()
        url = f"http://{hostname}"

        result = validator.validate([url])

        assert url in result.valid_urls

    @given(
        label=st.text(
            alphabet=string.ascii_lowercase + string.digits + "-",
            min_size=1,
            max_size=10,
        )
    )
    @settings(max_examples=100)
    def test_hostname_without_dot_rejected(self, label):
        """Hostnames without any dot are rejected."""
        # Ensure no dots in the label
        assume("." not in label)
        validator = URLValidator()
        url = f"http://{label}"

        result = validator.validate([url])

        assert len(result.valid_urls) == 0
        assert len(result.invalid_entries) == 1

    @given(
        hostname=st.one_of(
            # Leading dot: .label
            valid_hostname_label().map(lambda l: f".{l}"),
            # Trailing dot: label.
            valid_hostname_label().map(lambda l: f"{l}."),
            # Consecutive dots: label..label
            st.tuples(valid_hostname_label(), valid_hostname_label()).map(
                lambda t: f"{t[0]}..{t[1]}"
            ),
        )
    )
    @settings(max_examples=100)
    def test_hostname_with_empty_labels_rejected(self, hostname):
        """Hostnames with empty labels (leading/trailing/consecutive dots) are rejected."""
        validator = URLValidator()
        url = f"http://{hostname}"

        result = validator.validate([url])

        assert len(result.valid_urls) == 0
        assert len(result.invalid_entries) == 1

    @given(
        base_hostname=valid_hostname(),
        special_char=st.sampled_from(["!", "^", "&", "*", "(", ")", " ", "+", "=", "~"]),
    )
    @settings(max_examples=100)
    def test_hostname_with_special_chars_rejected(self, base_hostname, special_char):
        """Hostnames with characters other than alphanumeric, hyphens, and dots are rejected.

        Note: Characters like @, #, $, %, :, / have special URL semantics in RFC 3986
        (userinfo separator, fragment, query, port, path) and would be parsed by urlparse
        as structural delimiters rather than appearing in the hostname. We test only
        characters that actually end up in the parsed hostname component.
        """
        validator = URLValidator()
        # Insert a special char into the hostname
        invalid_hostname = base_hostname[:1] + special_char + base_hostname[1:]
        url = f"http://{invalid_hostname}"

        result = validator.validate([url])

        assert len(result.valid_urls) == 0
        assert len(result.invalid_entries) == 1


class TestProperty6ValidationPartition:
    """Property 6: Validation correctly partitions URLs

    Feature: browser-automation-framework, Property 6: Validation correctly partitions URLs

    For any list of URL strings, the URL_Validator SHALL partition the
    list such that: (a) every URL in the valid output has a correct scheme
    and valid hostname, (b) every URL in the invalid output has a non-empty
    reason string, and (c) the union of valid and invalid entries (by original
    URL) equals the deduplicated input set.

    **Validates: Requirements 2.4, 2.5, 2.6**
    """

    @given(
        valid_urls=st.lists(valid_url(), min_size=1, max_size=5),
        invalid_urls=st.lists(
            st.one_of(
                # Missing scheme
                st.from_regex(r"[a-z]{3,8}\.[a-z]{2,4}", fullmatch=True),
                # Invalid scheme
                st.tuples(
                    st.sampled_from(["ftp", "file", "ssh", "telnet"]),
                    valid_hostname(),
                ).map(lambda t: f"{t[0]}://{t[1]}"),
                # Empty string
                st.just(""),
            ),
            min_size=1,
            max_size=5,
        ),
    )
    @settings(max_examples=100)
    def test_partition_covers_all_unique_inputs(self, valid_urls, invalid_urls):
        """Validates: Requirements 2.4, 2.5, 2.6"""
        validator = URLValidator()
        all_urls = valid_urls + invalid_urls

        result = validator.validate(all_urls)

        # Compute the deduplicated set (trimmed) from the input
        seen = set()
        deduplicated = []
        for url in all_urls:
            trimmed = url.strip()
            if trimmed not in seen:
                seen.add(trimmed)
                deduplicated.append(trimmed)

        # The union of valid + invalid URLs should equal the deduplicated input
        valid_set = set(result.valid_urls)
        invalid_set = set(entry[0] for entry in result.invalid_entries)
        result_union = valid_set | invalid_set

        assert result_union == set(deduplicated)

    @given(
        valid_urls=st.lists(valid_url(), min_size=1, max_size=5),
        invalid_urls=st.lists(
            st.one_of(
                st.tuples(
                    st.sampled_from(["ftp", "file", "ssh"]),
                    valid_hostname(),
                ).map(lambda t: f"{t[0]}://{t[1]}"),
                st.just(""),
            ),
            min_size=1,
            max_size=5,
        ),
    )
    @settings(max_examples=100)
    def test_invalid_entries_have_nonempty_reason(self, valid_urls, invalid_urls):
        """Every invalid entry must have a non-empty reason string."""
        validator = URLValidator()
        all_urls = valid_urls + invalid_urls

        result = validator.validate(all_urls)

        for url, reason in result.invalid_entries:
            assert reason != "", f"Invalid URL '{url}' has empty reason"
            assert len(reason) > 0
