"""
Download history persistence using JSON.

Maintains a list of the last 5 downloads with:
- Title
- Output path
- Status
- Format
- Completion timestamp
"""

import json
import threading
from pathlib import Path

from src.domain.models import HistoryEntry
from src.infra.platform import get_history_file_path

MAX_HISTORY_ENTRIES = 5


class HistoryStore:
    """
    Persistent storage for download history.

    Stores the last 5 download entries in a JSON file.
    Uses FIFO (First In, First Out) when limit is reached.
    """

    def __init__(self, history_path: Path | None = None):
        """
        Initialize the history store.

        Args:
            history_path: Optional custom path for history file.
                         Uses default app data location if not provided.
        """
        self._history_path = history_path or get_history_file_path()
        self._entries: list[HistoryEntry] | None = None
        self._lock = threading.RLock()

    def load(self) -> list[HistoryEntry]:
        """
        Load history from disk.

        Returns:
            List of HistoryEntry objects (empty list if file doesn't exist)
        """
        with self._lock:
            if self._entries is not None:
                return list(self._entries)

            try:
                if self._history_path.exists():
                    content = self._history_path.read_text(encoding="utf-8")
                    data = json.loads(content)

                    entries_data = data.get("entries", [])
                    if not isinstance(entries_data, list):
                        raise ValueError("Invalid history list")
                    self._entries = []
                    for entry in entries_data:
                        try:
                            self._entries.append(HistoryEntry.from_dict(entry))
                        except (KeyError, TypeError, ValueError):
                            continue
                    self._entries = self._entries[:MAX_HISTORY_ENTRIES]
                else:
                    self._entries = []

            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                # Corrupted history, start fresh
                self._entries = []

            return list(self._entries)

    def save(self, entries: list[HistoryEntry]) -> bool:
        """
        Save history entries to disk.

        Args:
            entries: List of HistoryEntry objects to save

        Returns:
            True if saved successfully, False otherwise
        """
        with self._lock:
            try:
                # Ensure directory exists
                self._history_path.parent.mkdir(parents=True, exist_ok=True)

                # Prepare data
                data = {
                    "version": 1,
                    "entries": [entry.to_dict() for entry in entries],
                }

                # Write atomically
                content = json.dumps(data, indent=2, ensure_ascii=False)
                temp_path = self._history_path.with_suffix(".tmp")
                temp_path.write_text(content, encoding="utf-8")
                temp_path.replace(self._history_path)

                # Update cache
                self._entries = list(entries)

                return True

            except Exception:
                return False

    def add(self, entry: HistoryEntry) -> None:
        """
        Add a new entry to history.

        Maintains maximum of 5 entries using FIFO:
        - New entry is added at the beginning
        - Oldest entry is removed if limit exceeded

        Args:
            entry: The HistoryEntry to add
        """
        with self._lock:
            entries = self.load()

            # Add new entry at the beginning
            entries.insert(0, entry)

            # Enforce limit (keep only the newest entries)
            if len(entries) > MAX_HISTORY_ENTRIES:
                entries = entries[:MAX_HISTORY_ENTRIES]

            self.save(entries)

    def clear(self) -> bool:
        """
        Clear all history entries.

        Returns:
            True if cleared successfully, False otherwise
        """
        with self._lock:
            self._entries = []
            return self.save([])

    def get_entries(self) -> list[HistoryEntry]:
        """
        Get all history entries.

        Returns:
            List of HistoryEntry objects (most recent first)
        """
        with self._lock:
            return self.load()
