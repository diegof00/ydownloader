"""
Domain Layer - Business logic without I/O dependencies.

This layer contains:
- Models (Download, HistoryEntry, Settings, enums)
- Services (DownloadService, URLValidator)
- Domain exceptions

The domain layer is independent of UI and infrastructure concerns,
making it easy to test and potentially reuse in other contexts (CLI, web).
"""

from src.domain.models import (
    Download,
    DownloadFormat,
    DownloadStatus,
    HistoryEntry,
    Settings,
)
from src.domain.errors import (
    DomainError,
    InvalidURLError,
    UnsupportedSiteError,
    DownloadError,
    PermissionError,
    DiskSpaceError,
    CancelledException,
    ContentUnavailableError,
)

__all__ = [
    # Models
    "Download",
    "DownloadFormat",
    "DownloadStatus",
    "HistoryEntry",
    "Settings",
    # Errors
    "DomainError",
    "InvalidURLError",
    "UnsupportedSiteError",
    "DownloadError",
    "PermissionError",
    "DiskSpaceError",
    "CancelledException",
    "ContentUnavailableError",
]
