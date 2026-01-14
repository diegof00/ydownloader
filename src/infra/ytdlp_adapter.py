"""
yt-dlp adapter for download operations.

Wraps yt-dlp functionality with:
- Progress hooks for UI updates
- Cancellation support via threading.Event
- Format selection (video/audio)
- Safe argument passing (no shell injection)
"""

import threading
from pathlib import Path
from typing import Callable, Optional

from src.domain.models import DownloadFormat
from src.domain.errors import (
    DownloadError,
    CancelledException,
    ContentUnavailableError,
)


class YtdlpAdapter:
    """
    Adapter for yt-dlp download operations.

    Provides a safe interface to yt-dlp with:
    - Progress reporting via callbacks
    - Cancellation support
    - Format conversion (video/audio)
    """

    def __init__(self):
        """Initialize the adapter."""
        self._cancel_event = threading.Event()
        self._current_filename: Optional[str] = None

    def download(
        self,
        url: str,
        output_folder: Path,
        format: DownloadFormat,
        on_progress: Callable[[dict], None],
    ) -> Path:
        """
        Download content from URL.

        Args:
            url: URL to download
            output_folder: Folder to save the file
            format: VIDEO or AUDIO format
            on_progress: Callback for progress updates

        Returns:
            Path to the downloaded file

        Raises:
            DownloadError: If download fails
            CancelledException: If download is cancelled
            ContentUnavailableError: If content is not available
        """
        import yt_dlp

        self._cancel_event.clear()
        self._current_filename = None
        downloaded_file: Optional[Path] = None

        def progress_hook(d):
            # Check for cancellation
            if self._cancel_event.is_set():
                raise CancelledException()

            status = d.get("status", "")

            if status == "downloading":
                # Calculate progress percentage
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
                downloaded = d.get("downloaded_bytes", 0)

                if total > 0:
                    percent = int((downloaded / total) * 100)
                else:
                    percent = 0

                on_progress({
                    "percent": percent,
                    "status": "downloading",
                    "title": d.get("info_dict", {}).get("title"),
                    "eta": d.get("eta"),
                    "speed": d.get("_speed_str"),
                })

            elif status == "finished":
                self._current_filename = d.get("filename")
                on_progress({
                    "percent": 100,
                    "status": "processing",
                    "title": d.get("info_dict", {}).get("title"),
                })

        # Configure yt-dlp options
        ydl_opts = self._get_options(output_folder, format, progress_hook)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first to get title
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise ContentUnavailableError(url)

                title = info.get("title", "video")
                on_progress({
                    "percent": 0,
                    "status": "connecting",
                    "title": title,
                })

                # Check for cancellation before starting
                if self._cancel_event.is_set():
                    raise CancelledException()

                # Download
                ydl.download([url])

            # Find the downloaded file
            if self._current_filename:
                downloaded_file = Path(self._current_filename)
            else:
                # Try to find the file by pattern
                ext = "mp3" if format == DownloadFormat.AUDIO else "mp4"
                candidates = list(output_folder.glob(f"*{title}*.{ext}"))
                if candidates:
                    downloaded_file = candidates[0]

            if downloaded_file and downloaded_file.exists():
                return downloaded_file
            else:
                raise DownloadError(
                    "Download completed but file not found",
                    "La descarga se completó pero no se encontró el archivo.",
                )

        except CancelledException:
            # Clean up partial files
            self._cleanup_partial(output_folder)
            raise

        except yt_dlp.utils.DownloadError as e:
            error_str = str(e).lower()

            if "private" in error_str or "unavailable" in error_str:
                raise ContentUnavailableError(url)

            if "network" in error_str or "connection" in error_str:
                raise DownloadError(
                    str(e),
                    "Error de conexión. Verifica tu conexión a internet e intenta de nuevo.",
                )

            raise DownloadError(str(e))

        except Exception as e:
            if isinstance(e, (CancelledException, DownloadError, ContentUnavailableError)):
                raise
            raise DownloadError(str(e))

    def cancel(self) -> None:
        """Signal cancellation of the current download."""
        self._cancel_event.set()

    def validate_url(self, url: str) -> tuple[bool, str]:
        """
        Validate if URL is supported by yt-dlp.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            import yt_dlp

            extractors = yt_dlp.extractor.gen_extractors()
            for extractor in extractors:
                if hasattr(extractor, "suitable") and extractor.suitable(url):
                    return True, ""

            return False, "Este sitio no está soportado actualmente."

        except Exception as e:
            return False, str(e)

    def _get_options(
        self,
        output_folder: Path,
        format: DownloadFormat,
        progress_hook: Callable,
    ) -> dict:
        """
        Build yt-dlp options dictionary.

        Args:
            output_folder: Target folder for downloads
            format: VIDEO or AUDIO format
            progress_hook: Progress callback function

        Returns:
            Dictionary of yt-dlp options
        """
        # Output template
        outtmpl = str(output_folder / "%(title)s.%(ext)s")

        # Base options
        opts = {
            "outtmpl": outtmpl,
            "progress_hooks": [progress_hook],
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            # Security: never use shell
            "no_color": True,
        }

        if format == DownloadFormat.AUDIO:
            # Audio-only: best audio, convert to MP3
            opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
        else:
            # Video: best quality with audio
            opts.update({
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
            })

        return opts

    def _cleanup_partial(self, folder: Path) -> None:
        """
        Clean up partial download files.

        Args:
            folder: Folder to clean up
        """
        try:
            patterns = ["*.part", "*.ytdl", "*.temp"]
            for pattern in patterns:
                for file in folder.glob(pattern):
                    try:
                        file.unlink()
                    except Exception:
                        pass
        except Exception:
            pass
