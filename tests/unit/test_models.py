"""
Unit tests for domain models.
"""

import pytest
from datetime import datetime
from pathlib import Path

from src.domain.models import (
    Download,
    DownloadFormat,
    DownloadStatus,
    HistoryEntry,
    Settings,
)


class TestDownloadFormat:
    """Tests for DownloadFormat enum."""

    def test_video_format_value(self):
        """Test VIDEO format has correct value."""
        assert DownloadFormat.VIDEO.value == "video"

    def test_audio_format_value(self):
        """Test AUDIO format has correct value."""
        assert DownloadFormat.AUDIO.value == "audio"


class TestDownloadStatus:
    """Tests for DownloadStatus enum."""

    def test_all_status_values(self):
        """Test all status enum values are correct."""
        assert DownloadStatus.PENDING.value == "pending"
        assert DownloadStatus.CONNECTING.value == "connecting"
        assert DownloadStatus.DOWNLOADING.value == "downloading"
        assert DownloadStatus.PROCESSING.value == "processing"
        assert DownloadStatus.COMPLETED.value == "completed"
        assert DownloadStatus.CANCELLED.value == "cancelled"
        assert DownloadStatus.ERROR.value == "error"


class TestDownload:
    """Tests for the Download dataclass."""

    @pytest.fixture
    def sample_download(self, tmp_path):
        """Create a sample download for testing."""
        return Download(
            url="https://www.youtube.com/watch?v=test",
            output_path=tmp_path / "video.mp4",
            format=DownloadFormat.VIDEO,
        )

    def test_download_creation(self, sample_download):
        """Test creating a download with required fields."""
        assert sample_download.url == "https://www.youtube.com/watch?v=test"
        assert sample_download.format == DownloadFormat.VIDEO
        assert sample_download.status == DownloadStatus.PENDING
        assert sample_download.progress == 0
        assert sample_download.id is not None

    def test_download_has_uuid(self, sample_download):
        """Test that download has a valid UUID."""
        # UUID should be a string with dashes
        assert len(sample_download.id) == 36
        assert sample_download.id.count("-") == 4

    def test_download_progress_validation(self, tmp_path):
        """Test that progress is validated to be 0-100."""
        with pytest.raises(ValueError):
            Download(
                url="https://example.com",
                output_path=tmp_path / "video.mp4",
                format=DownloadFormat.VIDEO,
                progress=150,
            )

    def test_download_progress_negative_validation(self, tmp_path):
        """Test that negative progress raises error."""
        with pytest.raises(ValueError):
            Download(
                url="https://example.com",
                output_path=tmp_path / "video.mp4",
                format=DownloadFormat.VIDEO,
                progress=-10,
            )

    def test_update_progress(self, sample_download):
        """Test updating download progress."""
        sample_download.update_progress(50, DownloadStatus.DOWNLOADING, "Test Title")
        assert sample_download.progress == 50
        assert sample_download.status == DownloadStatus.DOWNLOADING
        assert sample_download.title == "Test Title"

    def test_update_progress_clamps_to_100(self, sample_download):
        """Test that progress is clamped to 100."""
        sample_download.update_progress(150, DownloadStatus.DOWNLOADING)
        assert sample_download.progress == 100

    def test_update_progress_clamps_to_0(self, sample_download):
        """Test that progress is clamped to 0."""
        sample_download.update_progress(-50, DownloadStatus.DOWNLOADING)
        assert sample_download.progress == 0

    def test_mark_completed(self, sample_download):
        """Test marking download as completed."""
        sample_download.mark_completed()
        assert sample_download.status == DownloadStatus.COMPLETED
        assert sample_download.progress == 100
        assert sample_download.completed_at is not None

    def test_mark_error(self, sample_download):
        """Test marking download as error."""
        sample_download.mark_error("Connection failed")
        assert sample_download.status == DownloadStatus.ERROR
        assert sample_download.error_message == "Connection failed"
        assert sample_download.completed_at is not None

    def test_mark_cancelled(self, sample_download):
        """Test marking download as cancelled."""
        sample_download.mark_cancelled()
        assert sample_download.status == DownloadStatus.CANCELLED
        assert sample_download.completed_at is not None

    def test_is_active_for_pending(self, sample_download):
        """Test is_active returns True for pending downloads."""
        assert sample_download.is_active is True

    def test_is_active_for_downloading(self, sample_download):
        """Test is_active returns True for downloading."""
        sample_download.status = DownloadStatus.DOWNLOADING
        assert sample_download.is_active is True

    def test_is_active_for_completed(self, sample_download):
        """Test is_active returns False for completed."""
        sample_download.mark_completed()
        assert sample_download.is_active is False

    def test_is_terminal_for_completed(self, sample_download):
        """Test is_terminal returns True for completed."""
        sample_download.mark_completed()
        assert sample_download.is_terminal is True

    def test_is_terminal_for_pending(self, sample_download):
        """Test is_terminal returns False for pending."""
        assert sample_download.is_terminal is False


class TestHistoryEntry:
    """Tests for the HistoryEntry dataclass."""

    @pytest.fixture
    def completed_download(self, tmp_path):
        """Create a completed download for testing."""
        download = Download(
            url="https://www.youtube.com/watch?v=test",
            output_path=tmp_path / "video.mp4",
            format=DownloadFormat.VIDEO,
            title="Test Video",
        )
        download.mark_completed()
        return download

    def test_from_download(self, completed_download):
        """Test creating HistoryEntry from Download."""
        entry = HistoryEntry.from_download(completed_download)
        assert entry.id == completed_download.id
        assert entry.title == "Test Video"
        assert entry.status == "completed"
        assert entry.format == "video"

    def test_to_dict(self, completed_download):
        """Test converting HistoryEntry to dict."""
        entry = HistoryEntry.from_download(completed_download)
        data = entry.to_dict()
        assert "id" in data
        assert "title" in data
        assert "output_path" in data
        assert "status" in data
        assert "format" in data
        assert "completed_at" in data

    def test_from_dict(self):
        """Test creating HistoryEntry from dict."""
        data = {
            "id": "test-id",
            "title": "Test Video",
            "output_path": "/path/to/video.mp4",
            "status": "completed",
            "format": "video",
            "completed_at": "2026-01-13T12:00:00",
        }
        entry = HistoryEntry.from_dict(data)
        assert entry.id == "test-id"
        assert entry.title == "Test Video"


class TestSettings:
    """Tests for the Settings dataclass."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        assert settings.last_output_folder is None
        assert settings.default_format == "video"
        assert settings.show_disclaimer is True

    def test_to_dict(self):
        """Test converting Settings to dict."""
        settings = Settings(
            last_output_folder="/path/to/downloads",
            default_format="audio",
            show_disclaimer=False,
        )
        data = settings.to_dict()
        assert data["version"] == 1
        assert data["last_output_folder"] == "/path/to/downloads"
        assert data["default_format"] == "audio"
        assert data["show_disclaimer"] is False

    def test_from_dict(self):
        """Test creating Settings from dict."""
        data = {
            "version": 1,
            "last_output_folder": "/downloads",
            "default_format": "audio",
            "show_disclaimer": False,
        }
        settings = Settings.from_dict(data)
        assert settings.last_output_folder == "/downloads"
        assert settings.default_format == "audio"
        assert settings.show_disclaimer is False

    def test_from_dict_with_defaults(self):
        """Test from_dict uses defaults for missing keys."""
        data = {}
        settings = Settings.from_dict(data)
        assert settings.default_format == "video"
        assert settings.show_disclaimer is True
