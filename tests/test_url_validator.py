"""Unit tests for the URLValidator component.

Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
"""

import pytest

from browser_automation.url_validator import URLValidator


@pytest.fixture
def validator():
    """Provide a URLValidator instance."""
    return URLValidator()


class TestURLMissingSchemeRejected:
    """Test that a URL without a scheme is rejected."""

    def test_missing_scheme_is_invalid(self, validator):
        """A URL like 'www.example.com' without http/https should be rejected."""
        is_valid, reason = validator.is_valid_url("www.example.com")

        assert is_valid is False
        assert "scheme" in reason.lower()

    def test_missing_scheme_in_batch_validation(self, validator):
        """validate() should place a URL with missing scheme in invalid_entries."""
        result = validator.validate(["www.example.com"])

        assert len(result.valid_urls) == 0
        assert len(result.invalid_entries) == 1
        assert result.invalid_entries[0][0] == "www.example.com"
        assert "scheme" in result.invalid_entries[0][1].lower()


class TestURLFTPSchemeRejected:
    """Test that a URL with 'ftp' scheme is rejected."""

    def test_ftp_scheme_is_invalid(self, validator):
        """A URL with ftp:// scheme should be rejected."""
        is_valid, reason = validator.is_valid_url("ftp://files.example.com/data")

        assert is_valid is False
        assert "ftp" in reason.lower()

    def test_ftp_scheme_in_batch_validation(self, validator):
        """validate() should place ftp URLs in invalid_entries."""
        result = validator.validate(["ftp://files.example.com/data"])

        assert len(result.valid_urls) == 0
        assert len(result.invalid_entries) == 1
        assert "ftp" in result.invalid_entries[0][1].lower()


class TestURLInvalidHostnameCharactersRejected:
    """Test that a URL with invalid hostname characters is rejected."""

    def test_hostname_with_underscore_is_invalid(self, validator):
        """Hostnames containing underscores should be rejected."""
        is_valid, reason = validator.is_valid_url("http://invalid_host.example.com")

        assert is_valid is False
        assert "invalid characters" in reason.lower()

    def test_hostname_with_space_is_invalid(self, validator):
        """Hostnames containing spaces should be rejected."""
        is_valid, reason = validator.is_valid_url("http://bad host.com")

        assert is_valid is False
        # Either parsing fails or hostname is invalid
        assert is_valid is False


class TestURLNoDotInHostnameRejected:
    """Test that a URL with no dot in hostname is rejected."""

    def test_localhost_no_dot_is_invalid(self, validator):
        """A hostname like 'localhost' with no dot should be rejected."""
        is_valid, reason = validator.is_valid_url("http://localhost")

        assert is_valid is False
        assert "dot" in reason.lower()

    def test_single_word_hostname_is_invalid(self, validator):
        """A hostname like 'example' with no dot should be rejected."""
        is_valid, reason = validator.is_valid_url("http://example")

        assert is_valid is False
        assert "dot" in reason.lower()

    def test_no_dot_hostname_in_batch_validation(self, validator):
        """validate() should place a URL with no-dot hostname in invalid_entries."""
        result = validator.validate(["http://localhost"])

        assert len(result.valid_urls) == 0
        assert len(result.invalid_entries) == 1
        assert "dot" in result.invalid_entries[0][1].lower()


class TestValidURLWithAllComponentsAccepted:
    """Test that a valid URL with port, path, query, and fragment is accepted."""

    def test_full_url_with_all_components_is_valid(self, validator):
        """A URL with scheme, host, port, path, query, and fragment should pass."""
        url = "https://example.com:8080/path?query=value#fragment"
        is_valid, reason = validator.is_valid_url(url)

        assert is_valid is True
        assert reason == ""

    def test_full_url_in_batch_validation(self, validator):
        """validate() should include a fully-qualified URL in valid_urls."""
        url = "https://example.com:8080/path?query=value#fragment"
        result = validator.validate([url])

        assert len(result.valid_urls) == 1
        assert result.valid_urls[0] == url
        assert len(result.invalid_entries) == 0

    def test_http_url_is_also_valid(self, validator):
        """An http URL with port, path, query, and fragment should also pass."""
        url = "http://example.org:3000/api/users?page=1#top"
        is_valid, reason = validator.is_valid_url(url)

        assert is_valid is True
        assert reason == ""


class TestEmptyStringRejected:
    """Test that an empty string is rejected."""

    def test_empty_string_is_invalid(self, validator):
        """An empty string should be rejected with a descriptive reason."""
        is_valid, reason = validator.is_valid_url("")

        assert is_valid is False
        assert "empty" in reason.lower()

    def test_empty_string_in_batch_validation(self, validator):
        """validate() should place an empty string in invalid_entries."""
        result = validator.validate([""])

        assert len(result.valid_urls) == 0
        assert len(result.invalid_entries) == 1
        assert "empty" in result.invalid_entries[0][1].lower()


class TestWhitespaceOnlyStringRejected:
    """Test that a whitespace-only string is rejected."""

    def test_whitespace_only_is_invalid(self, validator):
        """A string of only spaces should be rejected as empty after trimming."""
        # After trimming, whitespace-only becomes empty
        is_valid, reason = validator.is_valid_url("   ")

        assert is_valid is False

    def test_whitespace_only_in_batch_validation(self, validator):
        """validate() should reject whitespace-only strings after trimming."""
        result = validator.validate(["   ", "\t\n"])

        assert len(result.valid_urls) == 0
        # After trimming, "   " becomes "" and "\t\n" also becomes ""
        # Since both trim to "", deduplication means only one invalid entry
        assert len(result.invalid_entries) >= 1
        assert all("empty" in reason.lower() for _, reason in result.invalid_entries)
