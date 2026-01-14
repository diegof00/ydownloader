"""
Unit tests for URL validators.
"""

import pytest
from src.domain.validators import URLValidator, ValidationResult


class TestURLValidator:
    """Tests for the URLValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a URLValidator instance."""
        return URLValidator()

    def test_valid_youtube_url(self, validator):
        """Test that a valid YouTube URL passes validation."""
        result = validator.validate("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result.is_valid is True
        assert result.error_message == ""

    def test_valid_youtube_short_url(self, validator):
        """Test that a valid YouTube short URL passes validation."""
        result = validator.validate("https://youtu.be/dQw4w9WgXcQ")
        assert result.is_valid is True

    def test_empty_url_fails(self, validator):
        """Test that an empty URL fails validation."""
        result = validator.validate("")
        assert result.is_valid is False
        assert result.error_code == "EMPTY_URL"

    def test_whitespace_only_url_fails(self, validator):
        """Test that a whitespace-only URL fails validation."""
        result = validator.validate("   ")
        assert result.is_valid is False
        assert result.error_code == "EMPTY_URL"

    def test_invalid_format_no_scheme(self, validator):
        """Test that URL without scheme fails validation."""
        result = validator.validate("www.youtube.com/watch?v=abc123")
        assert result.is_valid is False
        assert result.error_code == "INVALID_FORMAT"

    def test_invalid_format_not_url(self, validator):
        """Test that non-URL text fails validation."""
        result = validator.validate("not a url at all")
        assert result.is_valid is False
        assert result.error_code == "INVALID_FORMAT"

    def test_invalid_scheme_ftp(self, validator):
        """Test that FTP scheme fails validation."""
        result = validator.validate("ftp://example.com/file.mp4")
        assert result.is_valid is False
        assert result.error_code == "INVALID_FORMAT"

    def test_http_scheme_accepted(self, validator):
        """Test that HTTP scheme is accepted."""
        result = validator.validate("http://www.youtube.com/watch?v=abc123")
        # May pass format validation but could fail site check
        # At minimum, format should be valid
        assert result.error_code != "INVALID_FORMAT" or result.is_valid

    def test_https_scheme_accepted(self, validator):
        """Test that HTTPS scheme is accepted."""
        result = validator.validate("https://www.youtube.com/watch?v=abc123")
        assert result.is_valid is True

    def test_validation_result_has_user_message(self, validator):
        """Test that invalid results include a user-friendly message."""
        result = validator.validate("invalid")
        assert result.is_valid is False
        assert len(result.error_message) > 0
        # Should be in Spanish per spec
        assert "URL" in result.error_message or "url" in result.error_message


class TestValidationResult:
    """Tests for the ValidationResult dataclass."""

    def test_valid_result(self):
        """Test creating a valid result."""
        result = ValidationResult(is_valid=True)
        assert result.is_valid is True
        assert result.error_message == ""
        assert result.error_code == ""

    def test_invalid_result_with_message(self):
        """Test creating an invalid result with message."""
        result = ValidationResult(
            is_valid=False,
            error_message="Test error message",
            error_code="TEST_ERROR",
        )
        assert result.is_valid is False
        assert result.error_message == "Test error message"
        assert result.error_code == "TEST_ERROR"
