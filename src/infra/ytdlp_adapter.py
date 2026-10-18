"""
yt-dlp adapter for download operations.

Wraps yt-dlp functionality with:
- Progress hooks for UI updates
- Cancellation support via threading.Event
- Format selection (video/audio)
- Safe argument passing (no shell injection)
"""

import shutil
import tempfile
import threading
from collections.abc import Callable
from pathlib import Path

from src.domain.errors import (
    CancelledException,
    ContentUnavailableError,
    DownloadError,
)
from src.domain.models import DownloadFormat
from src.infra.file_system import FileSystem


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

        downloaded_file: Path | None = None

        if self._cancel_event.is_set():
            raise CancelledException()
        if not shutil.which("ffmpeg"):
            raise DownloadError(
                "FFmpeg is not installed",
                "FFmpeg no está instalado. Instálalo y verifica que esté disponible en el PATH.",
            )

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

                on_progress(
                    {
                        "percent": percent,
                        "status": "downloading",
                        "title": d.get("info_dict", {}).get("title"),
                        "eta": d.get("eta"),
                        "speed": d.get("_speed_str"),
                    }
                )

            elif status == "finished":
                on_progress(
                    {
                        "percent": 100,
                        "status": "processing",
                        "title": d.get("info_dict", {}).get("title"),
                    }
                )

        # Keep temporary files isolated so cancellation cannot remove other downloads.
        workspace = Path(tempfile.mkdtemp(prefix=".ydownloader-", dir=output_folder))
        ydl_opts = self._get_options(workspace, format, progress_hook)

        def finished_hook(filename):
            if self._cancel_event.is_set():
                raise CancelledException()
            nonlocal downloaded_file
            downloaded_file = Path(filename)

        # Runs after conversion and merging, with the actual final filename.
        ydl_opts["post_hooks"] = [finished_hook]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info is None or info.get("_type") in ("playlist", "multi_video"):
                    raise ContentUnavailableError(url)

            if self._cancel_event.is_set():
                raise CancelledException()

            if downloaded_file and downloaded_file.exists():
                destination = FileSystem().get_unique_filename(
                    output_folder, downloaded_file.stem, downloaded_file.suffix
                )
                shutil.move(str(downloaded_file), str(destination))
                return destination
            else:
                raise DownloadError(
                    "Download completed but file not found",
                    "La descarga se completó pero no se encontró el archivo.",
                )

        except CancelledException:
            raise

        except yt_dlp.utils.DownloadError as e:
            if self._cancel_event.is_set():
                raise CancelledException() from e
            error_str = str(e).lower()

            if any(token in error_str for token in ("sign in", "not a bot", "login required")):
                raise DownloadError(
                    str(e),
                    "El sitio exige iniciar sesión o verificar que no eres un bot. "
                    "Esta descarga requiere autenticación y no puede completarse sin ella.",
                ) from e

            if "private" in error_str or "unavailable" in error_str:
                raise ContentUnavailableError(url) from e

            if "network" in error_str or "connection" in error_str:
                raise DownloadError(
                    str(e),
                    "Error de conexión. Verifica tu conexión a internet e intenta de nuevo.",
                ) from e

            raise DownloadError(str(e)) from e

        except Exception as e:
            if isinstance(e, (CancelledException, DownloadError, ContentUnavailableError)):
                raise
            raise DownloadError(str(e)) from e

        finally:
            shutil.rmtree(workspace, ignore_errors=True)

    def prepare(self) -> None:
        """Reset cancellation before publishing a new job to the worker thread."""
        self._cancel_event.clear()

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
            "noplaylist": True,
            "socket_timeout": 15,
            "retries": 3,
            "extractor_retries": 3,
            "match_filter": self._reject_playlist,
            "postprocessor_hooks": [self._check_postprocessing_cancel],
            # Security: never use shell
            "no_color": True,
        }

        if format == DownloadFormat.AUDIO:
            # Audio-only: best audio, convert to MP3
            opts.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
            )
        else:
            # Video: best quality with audio
            opts.update(
                {
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                    "postprocessors": [
                        {
                            "key": "FFmpegVideoRemuxer",
                            "preferedformat": "mp4",
                        }
                    ],
                }
            )

        return opts

    @staticmethod
    def _reject_playlist(info, *, incomplete=False):
        if info.get("playlist_id") is not None:
            return "Selecciona un video individual, no una lista de reproducción."
        return None

    def _check_postprocessing_cancel(self, _):
        if self._cancel_event.is_set():
            raise CancelledException()
