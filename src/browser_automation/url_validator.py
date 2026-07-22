"""URL validation and deduplication for the Browser Automation Framework."""

import logging
import re
from urllib.parse import urlparse

from browser_automation.models import ValidationResult

logger = logging.getLogger(__name__)


class URLValidator:
    """Validates URL format, trims whitespace, deduplicates, and returns valid URLs."""

    # Hostname must contain only alphanumeric, hyphens, and dots.
    # Must have at least one dot separating non-empty labels.
    _HOSTNAME_CHAR_PATTERN = re.compile(r"^[a-zA-Z0-9\-\.]+$")

    def validate(self, urls: list[str]) -> ValidationResult:
        """
        Validate a list of raw URL strings.

        - Trims whitespace
        - Checks scheme (http/https)
        - Checks hostname format
        - Accepts optional port, path, query, fragment
        - Deduplicates preserving insertion order of first occurrence

        Returns ValidationResult with valid URLs and invalid entries with reasons.
        """
        valid_urls: list[str] = []
        invalid_entries: list[tuple[str, str]] = []
        seen: set[str] = set()

        for raw_url in urls:
            # Trim leading/trailing whitespace
            trimmed = raw_url.strip()

            # Deduplication: skip if already processed
            if trimmed in seen:
                continue
            seen.add(trimmed)

            # Validate the URL
            is_valid, reason = self.is_valid_url(trimmed)

            if is_valid:
                valid_urls.append(trimmed)
            else:
                invalid_entries.append((trimmed, reason))
                logger.warning("Invalid URL skipped: '%s' - Reason: %s", trimmed, reason)

        return ValidationResult(valid_urls=valid_urls, invalid_entries=invalid_entries)

    def is_valid_url(self, url: str) -> tuple[bool, str]:
        """
        Validate a single URL.

        Returns (is_valid, reason_if_invalid).
        A reason of empty string indicates the URL is valid.
        """
        # Check for empty or whitespace-only input
        if not url:
            return False, "URL is empty"

        # Parse the URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, f"URL parsing failed: {e}"

        # Validate scheme is exactly http or https
        if parsed.scheme not in ("http", "https"):
            if not parsed.scheme:
                return False, "URL is missing a scheme (must be http or https)"
            return False, f"Invalid scheme '{parsed.scheme}' (must be http or https)"

        # Extract hostname (netloc may include port)
        hostname = parsed.hostname
        if not hostname:
            return False, "URL is missing a hostname"

        # Validate hostname characters: only alphanumeric, hyphens, and dots
        if not self._HOSTNAME_CHAR_PATTERN.match(hostname):
            return False, (
                f"Hostname '{hostname}' contains invalid characters "
                "(only alphanumeric, hyphens, and dots allowed)"
            )

        # Validate hostname has at least one dot separating non-empty labels
        labels = hostname.split(".")
        if len(labels) < 2:
            return False, (
                f"Hostname '{hostname}' must contain at least one dot "
                "separating a domain and top-level domain"
            )

        # Check all labels are non-empty (no leading/trailing/consecutive dots)
        for label in labels:
            if not label:
                return False, (
                    f"Hostname '{hostname}' has empty labels "
                    "(no leading, trailing, or consecutive dots allowed)"
                )

        return True, ""
