"""
Platform-specific utilities for YDownloader.

Provides OS-independent access to system folders and platform detection.
"""

import platform
from pathlib import Path
from typing import Optional


def get_os_name() -> str:
    """Get the current operating system name."""
    return platform.system().lower()


def get_downloads_folder() -> Path:
    """
    Get the system Downloads folder for the current user.

    Returns:
        Path to the Downloads folder
    """
    home = Path.home()

    if get_os_name() == "windows":
        # Windows: try known locations
        downloads = home / "Downloads"
        if downloads.exists():
            return downloads
        # Fallback to home directory
        return home

    elif get_os_name() == "darwin":
        # macOS
        downloads = home / "Downloads"
        if downloads.exists():
            return downloads
        return home

    else:
        # Linux and other Unix-like systems
        # Check XDG user directories first
        xdg_download = _get_xdg_download_dir()
        if xdg_download and xdg_download.exists():
            return xdg_download

        # Fallback to ~/Downloads
        downloads = home / "Downloads"
        if downloads.exists():
            return downloads

        return home


def get_app_data_folder() -> Path:
    """
    Get the application data folder for storing config and history.

    Creates the folder if it doesn't exist.

    Returns:
        Path to the app data folder (~/.ydownloader/ or platform equivalent)
    """
    home = Path.home()

    if get_os_name() == "windows":
        # Windows: %APPDATA%\YDownloader
        app_data = Path.home() / "AppData" / "Roaming" / "YDownloader"

    elif get_os_name() == "darwin":
        # macOS: ~/Library/Application Support/YDownloader
        app_data = home / "Library" / "Application Support" / "YDownloader"

    else:
        # Linux: ~/.config/ydownloader (XDG compliant)
        xdg_config = Path.home() / ".config"
        app_data = xdg_config / "ydownloader"

    # Create directory if it doesn't exist
    app_data.mkdir(parents=True, exist_ok=True)

    return app_data


def _get_xdg_download_dir() -> Optional[Path]:
    """
    Get XDG user download directory on Linux.

    Returns:
        Path to XDG download directory, or None if not configured
    """
    import os

    # Check XDG_DOWNLOAD_DIR environment variable
    xdg_download = os.environ.get("XDG_DOWNLOAD_DIR")
    if xdg_download:
        return Path(xdg_download)

    # Try to read from user-dirs.dirs
    user_dirs_file = Path.home() / ".config" / "user-dirs.dirs"
    if user_dirs_file.exists():
        try:
            content = user_dirs_file.read_text()
            for line in content.splitlines():
                if line.startswith("XDG_DOWNLOAD_DIR"):
                    # Parse: XDG_DOWNLOAD_DIR="$HOME/Downloads"
                    value = line.split("=", 1)[1].strip().strip('"')
                    value = value.replace("$HOME", str(Path.home()))
                    return Path(value)
        except Exception:
            pass

    return None


def get_config_file_path() -> Path:
    """Get path to the configuration file."""
    return get_app_data_folder() / "config.json"


def get_history_file_path() -> Path:
    """Get path to the history file."""
    return get_app_data_folder() / "history.json"
