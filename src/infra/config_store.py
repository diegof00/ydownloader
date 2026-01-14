"""
Configuration persistence using JSON.

Stores user preferences between sessions:
- Last output folder
- Default format preference
- Disclaimer shown status
"""

import json
from pathlib import Path
from typing import Optional

from src.domain.models import Settings, DownloadFormat
from src.infra.platform import get_config_file_path


class ConfigStore:
    """
    Persistent storage for user configuration.

    Stores settings in a JSON file in the app data folder.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the config store.

        Args:
            config_path: Optional custom path for config file.
                        Uses default app data location if not provided.
        """
        self._config_path = config_path or get_config_file_path()
        self._settings: Optional[Settings] = None

    def load(self) -> Settings:
        """
        Load settings from disk.

        Returns:
            Settings object (with defaults if file doesn't exist)
        """
        if self._settings is not None:
            return self._settings

        try:
            if self._config_path.exists():
                content = self._config_path.read_text(encoding="utf-8")
                data = json.loads(content)
                self._settings = Settings.from_dict(data)
            else:
                self._settings = Settings()

        except (json.JSONDecodeError, KeyError, TypeError):
            # Corrupted config, use defaults
            self._settings = Settings()

        return self._settings

    def save(self) -> bool:
        """
        Save current settings to disk.

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            settings = self.load()

            # Ensure directory exists
            self._config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write atomically
            content = json.dumps(settings.to_dict(), indent=2, ensure_ascii=False)
            temp_path = self._config_path.with_suffix(".tmp")
            temp_path.write_text(content, encoding="utf-8")
            temp_path.replace(self._config_path)

            return True

        except Exception:
            return False

    def get_last_output_folder(self) -> Optional[Path]:
        """
        Get the last used output folder.

        Returns:
            Path to the folder, or None if not set or doesn't exist
        """
        settings = self.load()
        if settings.last_output_folder:
            folder = Path(settings.last_output_folder)
            if folder.exists() and folder.is_dir():
                return folder
        return None

    def set_last_output_folder(self, folder: Path) -> None:
        """
        Save the last used output folder.

        Args:
            folder: Path to save
        """
        settings = self.load()
        settings.last_output_folder = str(folder)
        self.save()

    def get_default_format(self) -> DownloadFormat:
        """
        Get the default download format.

        Returns:
            DownloadFormat.VIDEO or DownloadFormat.AUDIO
        """
        settings = self.load()
        if settings.default_format == "audio":
            return DownloadFormat.AUDIO
        return DownloadFormat.VIDEO

    def set_default_format(self, format: DownloadFormat) -> None:
        """
        Save the default download format.

        Args:
            format: Format to save as default
        """
        settings = self.load()
        settings.default_format = format.value
        self.save()

    def should_show_disclaimer(self) -> bool:
        """
        Check if legal disclaimer should be shown.

        Returns:
            True if disclaimer hasn't been shown yet
        """
        settings = self.load()
        return settings.show_disclaimer

    def mark_disclaimer_shown(self) -> None:
        """Mark the disclaimer as shown (won't show again)."""
        settings = self.load()
        settings.show_disclaimer = False
        self.save()
