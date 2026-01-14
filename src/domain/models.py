"""
Domain models for YDownloader.

Contains all data models, enums, and value objects used in the domain layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
import uuid


class DownloadFormat(Enum):
    """Format options for downloaded content."""

    VIDEO = "video"  # MP4 with video and audio
    AUDIO = "audio"  # Audio only, MP3


class DownloadStatus(Enum):
    """Status of a download operation."""

    PENDING = "pending"  # Created, not started
    CONNECTING = "connecting"  # Connecting to server
    DOWNLOADING = "downloading"  # Download in progress
    PROCESSING = "processing"  # Post-processing (conversion)
    COMPLETED = "completed"  # Finished successfully
    CANCELLED = "cancelled"  # Cancelled by user
    ERROR = "error"  # Error during download


@dataclass
class Download:
    """
    Represents an active or completed download operation.

    Attributes:
        id: Unique identifier for the download
        url: Original URL provided by user
        output_path: Full path of the output file
        format: Selected format (VIDEO or AUDIO)
        status: Current status of the download
        progress: Download progress percentage (0-100)
        title: Content title (extracted from metadata)
        error_message: Error message if status is ERROR
        started_at: Timestamp when download started
        completed_at: Timestamp when download finished
    """

    url: str
    output_path: Path
    format: DownloadFormat
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: DownloadStatus = DownloadStatus.PENDING
    progress: int = 0
    title: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate download data after initialization."""
        if not 0 <= self.progress <= 100:
            raise ValueError(f"Progress must be between 0 and 100, got {self.progress}")

    def update_progress(self, percent: int, status: DownloadStatus, title: Optional[str] = None):
        """
        Update download progress.

        Args:
            percent: New progress percentage (0-100)
            status: New status
            title: Optional title update
        """
        self.progress = max(0, min(100, percent))
        self.status = status
        if title:
            self.title = title

    def mark_completed(self):
        """Mark download as successfully completed."""
        self.status = DownloadStatus.COMPLETED
        self.progress = 100
        self.completed_at = datetime.now()

    def mark_error(self, message: str):
        """Mark download as failed with error message."""
        self.status = DownloadStatus.ERROR
        self.error_message = message
        self.completed_at = datetime.now()

    def mark_cancelled(self):
        """Mark download as cancelled by user."""
        self.status = DownloadStatus.CANCELLED
        self.completed_at = datetime.now()

    @property
    def is_active(self) -> bool:
        """Return True if download is currently in progress."""
        return self.status in (
            DownloadStatus.PENDING,
            DownloadStatus.CONNECTING,
            DownloadStatus.DOWNLOADING,
            DownloadStatus.PROCESSING,
        )

    @property
    def is_terminal(self) -> bool:
        """Return True if download has reached a terminal state."""
        return self.status in (
            DownloadStatus.COMPLETED,
            DownloadStatus.CANCELLED,
            DownloadStatus.ERROR,
        )


@dataclass
class HistoryEntry:
    """
    Simplified download record for history persistence.

    This is a serializable version of Download with only the
    information needed for the history display.
    """

    id: str
    title: str
    output_path: str  # String for JSON serialization
    status: str  # "completed", "cancelled", "error"
    format: str  # "video" or "audio"
    completed_at: str  # ISO 8601 timestamp

    @classmethod
    def from_download(cls, download: Download) -> "HistoryEntry":
        """
        Create a HistoryEntry from a completed Download.

        Args:
            download: The completed download to convert

        Returns:
            A new HistoryEntry instance
        """
        return cls(
            id=download.id,
            title=download.title or "Sin título",
            output_path=str(download.output_path),
            status=download.status.value,
            format=download.format.value,
            completed_at=download.completed_at.isoformat() if download.completed_at else "",
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "output_path": self.output_path,
            "status": self.status,
            "format": self.format,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryEntry":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            id=data["id"],
            title=data["title"],
            output_path=data["output_path"],
            status=data["status"],
            format=data["format"],
            completed_at=data["completed_at"],
        )


@dataclass
class Settings:
    """
    User preferences persisted between sessions.

    Attributes:
        last_output_folder: Last folder selected for downloads
        default_format: Default format preference
        show_disclaimer: Whether to show legal disclaimer on startup
    """

    last_output_folder: Optional[str] = None
    default_format: str = "video"
    show_disclaimer: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": 1,
            "last_output_folder": self.last_output_folder,
            "default_format": self.default_format,
            "show_disclaimer": self.show_disclaimer,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        """Create from dictionary (JSON deserialization)."""
        return cls(
            last_output_folder=data.get("last_output_folder"),
            default_format=data.get("default_format", "video"),
            show_disclaimer=data.get("show_disclaimer", True),
        )
