"""
Unit tests for DownloadService.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from src.domain.models import Download, DownloadFormat, DownloadStatus
from src.domain.download_service import DownloadService
from src.domain.errors import InvalidURLError, PermissionError


class TestDownloadService:
    """Tests for the DownloadService class."""

    @pytest.fixture
    def mock_validator(self):
        """Create a mock URL validator."""
        validator = Mock()
        validator.validate.return_value = Mock(is_valid=True, error_message="")
        return validator

    @pytest.fixture
    def mock_downloader(self):
        """Create a mock downloader adapter."""
        downloader = Mock()
        downloader.download.return_value = Path("/output/video.mp4")
        return downloader

    @pytest.fixture
    def mock_file_system(self):
        """Create a mock file system adapter."""
        fs = Mock()
        fs.can_write.return_value = True
        fs.get_available_space.return_value = 1024 * 1024 * 1024  # 1GB
        fs.get_unique_filename.return_value = Path("/output/video.mp4")
        return fs

    @pytest.fixture
    def mock_history_store(self):
        """Create a mock history store."""
        store = Mock()
        return store

    @pytest.fixture
    def service(self, mock_validator, mock_downloader, mock_file_system, mock_history_store):
        """Create a DownloadService with mocked dependencies."""
        return DownloadService(
            validator=mock_validator,
            downloader=mock_downloader,
            file_system=mock_file_system,
            history_store=mock_history_store,
        )

    def test_start_download_validates_url(self, service, mock_validator):
        """Test that start_download validates the URL first."""
        url = "https://www.youtube.com/watch?v=test"
        output_folder = Path("/output")

        service.start_download(
            url=url,
            output_folder=output_folder,
            format=DownloadFormat.VIDEO,
            on_progress=Mock(),
            on_complete=Mock(),
            on_error=Mock(),
        )

        mock_validator.validate.assert_called_once_with(url)

    def test_start_download_checks_permissions(self, service, mock_file_system):
        """Test that start_download checks folder permissions."""
        url = "https://www.youtube.com/watch?v=test"
        output_folder = Path("/output")

        service.start_download(
            url=url,
            output_folder=output_folder,
            format=DownloadFormat.VIDEO,
            on_progress=Mock(),
            on_complete=Mock(),
            on_error=Mock(),
        )

        mock_file_system.can_write.assert_called_once_with(output_folder)

    def test_start_download_calls_error_on_invalid_url(self, service, mock_validator):
        """Test that invalid URL triggers error callback."""
        mock_validator.validate.return_value = Mock(
            is_valid=False, error_message="URL inválida"
        )
        on_error = Mock()

        service.start_download(
            url="invalid",
            output_folder=Path("/output"),
            format=DownloadFormat.VIDEO,
            on_progress=Mock(),
            on_complete=Mock(),
            on_error=on_error,
        )

        on_error.assert_called_once()
        assert "URL" in on_error.call_args[0][0]

    def test_start_download_calls_error_on_no_permission(
        self, service, mock_file_system
    ):
        """Test that no write permission triggers error callback."""
        mock_file_system.can_write.return_value = False
        on_error = Mock()

        service.start_download(
            url="https://www.youtube.com/watch?v=test",
            output_folder=Path("/restricted"),
            format=DownloadFormat.VIDEO,
            on_progress=Mock(),
            on_complete=Mock(),
            on_error=on_error,
        )

        on_error.assert_called_once()
        assert "permiso" in on_error.call_args[0][0].lower()

    def test_start_download_returns_download_object(self, service):
        """Test that start_download returns a Download object."""
        result = service.start_download(
            url="https://www.youtube.com/watch?v=test",
            output_folder=Path("/output"),
            format=DownloadFormat.VIDEO,
            on_progress=Mock(),
            on_complete=Mock(),
            on_error=Mock(),
        )

        assert isinstance(result, Download)
        assert result.url == "https://www.youtube.com/watch?v=test"
        assert result.format == DownloadFormat.VIDEO

    def test_cancel_download_when_active(self, service, mock_downloader):
        """Test cancelling an active download."""
        # Start a download first
        download = service.start_download(
            url="https://www.youtube.com/watch?v=test",
            output_folder=Path("/output"),
            format=DownloadFormat.VIDEO,
            on_progress=Mock(),
            on_complete=Mock(),
            on_error=Mock(),
        )

        result = service.cancel_download(download.id)

        assert result is True
        mock_downloader.cancel.assert_called_once()

    def test_cancel_download_when_no_active(self, service):
        """Test cancelling when no download is active."""
        result = service.cancel_download("non-existent-id")
        assert result is False

    def test_get_current_download_returns_none_initially(self, service):
        """Test that get_current_download returns None when no download active."""
        result = service.get_current_download()
        assert result is None

    def test_only_one_download_at_a_time(self, service):
        """Test that only one download can be active at a time."""
        # Start first download
        download1 = service.start_download(
            url="https://www.youtube.com/watch?v=test1",
            output_folder=Path("/output"),
            format=DownloadFormat.VIDEO,
            on_progress=Mock(),
            on_complete=Mock(),
            on_error=Mock(),
        )

        # Try to start second download
        on_error = Mock()
        download2 = service.start_download(
            url="https://www.youtube.com/watch?v=test2",
            output_folder=Path("/output"),
            format=DownloadFormat.VIDEO,
            on_progress=Mock(),
            on_complete=Mock(),
            on_error=on_error,
        )

        # Second download should fail or be rejected
        # Implementation can either call error or return None
        assert download2 is None or on_error.called
