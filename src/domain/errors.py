"""
Domain exceptions for YDownloader.

All exceptions include a user-friendly message that can be displayed
directly to non-technical users without exposing technical details.
"""

from typing import Optional


class DomainError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str, user_message: str):
        """
        Initialize domain error.

        Args:
            message: Technical message for logging/debugging
            user_message: User-friendly message for display
        """
        super().__init__(message)
        self.user_message = user_message


class InvalidURLError(DomainError):
    """Raised when URL format is invalid."""

    def __init__(self, url: str = ""):
        super().__init__(
            message=f"Invalid URL format: {url}",
            user_message="La URL ingresada no es válida. Por favor verifica e intenta de nuevo.",
        )


class UnsupportedSiteError(DomainError):
    """Raised when the URL's site is not supported by yt-dlp."""

    def __init__(self, url: str = ""):
        super().__init__(
            message=f"Unsupported site for URL: {url}",
            user_message="Este sitio no está soportado actualmente.",
        )


class DownloadError(DomainError):
    """Raised when download fails due to network or server issues."""

    def __init__(self, message: str = "Download failed", user_message: Optional[str] = None):
        super().__init__(
            message=message,
            user_message=user_message
            or "Error de conexión. Verifica tu conexión a internet e intenta de nuevo.",
        )


class PermissionError(DomainError):
    """Raised when there are no write permissions for the target folder."""

    def __init__(self, folder: str = ""):
        super().__init__(
            message=f"No write permission for folder: {folder}",
            user_message="No tienes permiso para guardar archivos en esta carpeta. "
            "Por favor selecciona otra carpeta.",
        )


class DiskSpaceError(DomainError):
    """Raised when there is insufficient disk space."""

    def __init__(self, required: int = 0, available: int = 0):
        super().__init__(
            message=f"Insufficient disk space. Required: {required}, Available: {available}",
            user_message="No hay suficiente espacio en disco. "
            "Libera espacio o elige otra ubicación.",
        )


class CancelledException(DomainError):
    """Raised when download is cancelled by user."""

    def __init__(self):
        super().__init__(
            message="Download cancelled by user",
            user_message="Descarga cancelada.",
        )


class ContentUnavailableError(DomainError):
    """Raised when content is not available or has been removed."""

    def __init__(self, url: str = ""):
        super().__init__(
            message=f"Content unavailable at URL: {url}",
            user_message="El contenido no está disponible o fue eliminado.",
        )
