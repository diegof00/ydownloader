"""
Shared pytest fixtures for YDownloader tests.
"""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def sample_urls():
    """Sample URLs for testing validation."""
    return {
        "valid_youtube": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "valid_vimeo": "https://vimeo.com/123456789",
        "invalid_format": "not a url",
        "empty": "",
        "missing_scheme": "www.youtube.com/watch?v=abc123",
        "unsupported_site": "https://example.com/video.mp4",
    }


@pytest.fixture
def mock_download_progress():
    """Factory for creating mock download progress data."""
    def _create(percent: int = 50, status: str = "downloading", title: str = "Test Video"):
        return {
            "percent": percent,
            "status": status,
            "title": title,
            "eta": 60,
            "speed": "1.5 MiB/s",
        }
    return _create
