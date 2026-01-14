"""
File system operations adapter.

Provides platform-independent file system operations including:
- Write permission checks
- Disk space queries
- Unique filename generation
- File deletion
"""

import os
import shutil
from pathlib import Path
from typing import Optional

from src.infra.platform import get_downloads_folder, get_app_data_folder


class FileSystem:
    """
    Adapter for file system operations.

    All operations are designed to be safe and handle errors gracefully.
    """

    def can_write(self, folder: Path) -> bool:
        """
        Check if we have write permission for a folder.

        Args:
            folder: Path to the folder to check

        Returns:
            True if we can write to the folder, False otherwise
        """
        try:
            if not folder.exists():
                # Try to create it
                folder.mkdir(parents=True, exist_ok=True)

            # Try to create a test file
            test_file = folder / ".ydownloader_write_test"
            try:
                test_file.touch()
                test_file.unlink()
                return True
            except (PermissionError, OSError):
                return False

        except Exception:
            return False

    def get_available_space(self, folder: Path) -> int:
        """
        Get available disk space in bytes for a folder.

        Args:
            folder: Path to check space for

        Returns:
            Available space in bytes, or 0 if unable to determine
        """
        try:
            if not folder.exists():
                folder = folder.parent

            usage = shutil.disk_usage(folder)
            return usage.free

        except Exception:
            return 0

    def get_unique_filename(
        self, folder: Path, base_name: str, extension: str
    ) -> Path:
        """
        Generate a unique filename in the folder.

        If "video.mp4" exists, returns "video (1).mp4", etc.

        Args:
            folder: Target folder
            base_name: Base name for the file (without extension)
            extension: File extension (with or without dot)

        Returns:
            Path to a unique filename
        """
        # Normalize extension
        if extension and not extension.startswith("."):
            extension = f".{extension}"

        # Sanitize base name
        base_name = self._sanitize_filename(base_name)

        # Try original name first
        candidate = folder / f"{base_name}{extension}"
        if not candidate.exists():
            return candidate

        # Find unique name with suffix
        counter = 1
        while True:
            candidate = folder / f"{base_name} ({counter}){extension}"
            if not candidate.exists():
                return candidate
            counter += 1

            # Safety limit
            if counter > 9999:
                import uuid
                return folder / f"{base_name}_{uuid.uuid4().hex[:8]}{extension}"

    def delete_file(self, path: Path) -> bool:
        """
        Delete a file safely.

        Args:
            path: Path to the file to delete

        Returns:
            True if file was deleted or didn't exist, False on error
        """
        try:
            if path.exists():
                path.unlink()
            return True
        except Exception:
            return False

    def delete_partial_files(self, folder: Path, base_name: str) -> int:
        """
        Delete partial download files matching a base name.

        Args:
            folder: Folder to search in
            base_name: Base name to match

        Returns:
            Number of files deleted
        """
        deleted = 0
        try:
            patterns = [
                f"{base_name}*.part",
                f"{base_name}*.ytdl",
                f"{base_name}*.temp",
            ]

            for pattern in patterns:
                for file in folder.glob(pattern):
                    if self.delete_file(file):
                        deleted += 1

        except Exception:
            pass

        return deleted

    def get_downloads_folder(self) -> Path:
        """Get the system Downloads folder."""
        return get_downloads_folder()

    def get_app_data_folder(self) -> Path:
        """Get the application data folder."""
        return get_app_data_folder()

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename by removing invalid characters.

        Args:
            filename: The filename to sanitize

        Returns:
            Sanitized filename safe for all platforms
        """
        # Characters not allowed in filenames on various platforms
        invalid_chars = '<>:"/\\|?*'

        # Replace invalid characters with underscore
        result = filename
        for char in invalid_chars:
            result = result.replace(char, "_")

        # Remove leading/trailing spaces and dots
        result = result.strip(". ")

        # Limit length
        if len(result) > 200:
            result = result[:200]

        # Ensure we have something
        if not result:
            result = "download"

        return result
