"""
URL validation for YDownloader.

Provides two-phase validation:
1. Format validation: Check URL structure (scheme, host)
2. Site validation: Check if yt-dlp supports the site
"""

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class ValidationResult:
    """Result of URL validation."""

    is_valid: bool
    error_message: str = ""
    error_code: str = ""  # "INVALID_FORMAT", "UNSUPPORTED_SITE", "EMPTY_URL"


class URLValidator:
    """
    Validates URLs for download eligibility.

    Performs two-phase validation:
    1. Basic format check (scheme, netloc)
    2. yt-dlp extractor check (if available)
    """

    ALLOWED_SCHEMES = ("http", "https")

    def validate(self, url: str) -> ValidationResult:
        """
        Validate a URL for download.

        Args:
            url: The URL to validate

        Returns:
            ValidationResult with is_valid, error_message, and error_code
        """
        # Phase 1: Check for empty URL
        if not url or not url.strip():
            return ValidationResult(
                is_valid=False,
                error_message="Por favor ingresa una URL.",
                error_code="EMPTY_URL",
            )

        url = url.strip()

        # Phase 2: Format validation
        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in self.ALLOWED_SCHEMES:
                return ValidationResult(
                    is_valid=False,
                    error_message="La URL ingresada no es válida. "
                    "Por favor verifica e intenta de nuevo.",
                    error_code="INVALID_FORMAT",
                )

            # Check netloc (host)
            if not parsed.netloc:
                return ValidationResult(
                    is_valid=False,
                    error_message="La URL ingresada no es válida. "
                    "Por favor verifica e intenta de nuevo.",
                    error_code="INVALID_FORMAT",
                )

        except Exception:
            return ValidationResult(
                is_valid=False,
                error_message="La URL ingresada no es válida. "
                "Por favor verifica e intenta de nuevo.",
                error_code="INVALID_FORMAT",
            )

        # Phase 3: Check if site is supported by yt-dlp
        if not self._is_site_supported(url):
            return ValidationResult(
                is_valid=False,
                error_message="Este sitio no está soportado actualmente.",
                error_code="UNSUPPORTED_SITE",
            )

        return ValidationResult(is_valid=True)

    def _is_site_supported(self, url: str) -> bool:
        """
        Check if the URL's site is supported by yt-dlp.

        Args:
            url: The URL to check

        Returns:
            True if site is supported, False otherwise
        """
        try:
            import yt_dlp

            # Get all available extractors
            extractors = yt_dlp.extractor.gen_extractors()

            # Check if any extractor matches the URL
            for extractor in extractors:
                if hasattr(extractor, "suitable") and extractor.suitable(url):
                    return True

            return False

        except ImportError:
            # If yt-dlp is not available, allow the URL
            # and let the download phase handle the error
            return True
        except Exception:
            # On any error, be permissive and let download phase validate
            return True
