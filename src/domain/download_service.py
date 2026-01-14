"""
Download service orchestrating the download workflow.

This service coordinates:
- URL validation
- Permission checks
- Download delegation to infrastructure
- Progress reporting
- History management
"""

from pathlib import Path
from typing import Callable, Optional, Protocol
import threading

from src.domain.models import Download, DownloadFormat, DownloadStatus
from src.domain.validators import URLValidator, ValidationResult
from src.domain.errors import (
    CancelledException,
    PermissionError,
    DiskSpaceError,
)


class DownloaderProtocol(Protocol):
    """Protocol for download adapters."""

    def download(
        self,
        url: str,
        output_folder: Path,
        format: DownloadFormat,
        on_progress: Callable,
    ) -> Path: ...

    def cancel(self) -> None: ...


class FileSystemProtocol(Protocol):
    """Protocol for file system adapters."""

    def can_write(self, folder: Path) -> bool: ...
    def get_available_space(self, folder: Path) -> int: ...
    def get_unique_filename(self, folder: Path, name: str, ext: str) -> Path: ...
    def delete_file(self, path: Path) -> bool: ...


class HistoryStorageProtocol(Protocol):
    """Protocol for history storage."""

    def add(self, entry) -> None: ...


# Type aliases for callbacks
ProgressCallback = Callable[[int, DownloadStatus, Optional[str]], None]
CompleteCallback = Callable[[Download], None]
ErrorCallback = Callable[[str], None]


class DownloadService:
    """
    Service for managing downloads.

    Provides the main interface for starting, cancelling, and monitoring downloads.
    Only one download can be active at a time.
    """

    def __init__(
        self,
        validator: URLValidator,
        downloader: DownloaderProtocol,
        file_system: FileSystemProtocol,
        history_store: Optional[HistoryStorageProtocol] = None,
    ):
        """
        Initialize the download service.

        Args:
            validator: URL validator instance
            downloader: Download adapter (e.g., YtdlpAdapter)
            file_system: File system adapter
            history_store: Optional history storage for persistence
        """
        self._validator = validator
        self._downloader = downloader
        self._file_system = file_system
        self._history_store = history_store
        self._current_download: Optional[Download] = None
        self._download_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start_download(
        self,
        url: str,
        output_folder: Path,
        format: DownloadFormat,
        on_progress: ProgressCallback,
        on_complete: CompleteCallback,
        on_error: ErrorCallback,
    ) -> Optional[Download]:
        """
        Start a new download.

        Args:
            url: URL to download
            output_folder: Folder to save the file
            format: VIDEO or AUDIO format
            on_progress: Callback for progress updates (percent, status, title)
            on_complete: Callback when download completes
            on_error: Callback when error occurs (receives error message)

        Returns:
            The Download object if started, None if rejected
        """
        with self._lock:
            # Check if download is already in progress
            if self._current_download and self._current_download.is_active:
                on_error("Ya hay una descarga en progreso. Cancela la actual para iniciar otra.")
                return None

        # Validate URL
        validation = self._validator.validate(url)
        if not validation.is_valid:
            on_error(validation.error_message)
            return None

        # Check folder permissions
        if not self._file_system.can_write(output_folder):
            on_error(
                "No tienes permiso para guardar archivos en esta carpeta. "
                "Por favor selecciona otra carpeta."
            )
            return None

        # Create download object
        download = Download(
            url=url,
            output_path=output_folder / "downloading",  # Placeholder, will be updated
            format=format,
        )

        with self._lock:
            self._current_download = download

        # Start download in background thread
        self._download_thread = threading.Thread(
            target=self._execute_download,
            args=(download, output_folder, on_progress, on_complete, on_error),
            daemon=True,
        )
        self._download_thread.start()

        return download

    def _execute_download(
        self,
        download: Download,
        output_folder: Path,
        on_progress: ProgressCallback,
        on_complete: CompleteCallback,
        on_error: ErrorCallback,
    ):
        """
        Execute the download in a background thread.

        Args:
            download: The Download object to update
            output_folder: Folder to save the file
            on_progress: Progress callback
            on_complete: Completion callback
            on_error: Error callback
        """
        try:
            # Update status to connecting
            download.update_progress(0, DownloadStatus.CONNECTING)
            on_progress(0, DownloadStatus.CONNECTING, None)

            # Define internal progress handler
            def handle_progress(progress_info):
                percent = progress_info.get("percent", 0)
                title = progress_info.get("title")
                status = DownloadStatus.DOWNLOADING

                if progress_info.get("status") == "processing":
                    status = DownloadStatus.PROCESSING

                download.update_progress(percent, status, title)
                on_progress(percent, status, title)

            # Execute download
            output_path = self._downloader.download(
                url=download.url,
                output_folder=output_folder,
                format=download.format,
                on_progress=handle_progress,
            )

            # Update download with final path
            download.output_path = output_path
            download.mark_completed()

            # Add to history
            if self._history_store:
                from src.domain.models import HistoryEntry

                entry = HistoryEntry.from_download(download)
                self._history_store.add(entry)

            on_complete(download)

        except CancelledException:
            download.mark_cancelled()
            on_complete(download)

        except Exception as e:
            error_message = str(e)
            if hasattr(e, "user_message"):
                error_message = e.user_message

            download.mark_error(error_message)
            on_error(error_message)

        finally:
            with self._lock:
                if self._current_download and self._current_download.id == download.id:
                    if download.is_terminal:
                        pass  # Keep reference for history

    def cancel_download(self, download_id: str) -> bool:
        """
        Cancel an active download.

        Args:
            download_id: ID of the download to cancel

        Returns:
            True if download was cancelled, False if not found or not active
        """
        with self._lock:
            if not self._current_download:
                return False

            if self._current_download.id != download_id:
                return False

            if not self._current_download.is_active:
                return False

        # Cancel the downloader
        self._downloader.cancel()
        return True

    def get_current_download(self) -> Optional[Download]:
        """
        Get the current download if any.

        Returns:
            The current Download object or None
        """
        with self._lock:
            return self._current_download
