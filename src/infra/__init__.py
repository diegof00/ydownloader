"""
Infrastructure Layer - External adapters and I/O operations.

This layer contains:
- YtdlpAdapter: Wrapper for yt-dlp download operations
- FileSystem: File system operations (permissions, space, unique names)
- ConfigStore: Persistence of user configuration (JSON)
- HistoryStore: Persistence of download history (JSON)
- Platform: OS-specific utilities

All adapters implement protocols defined in the domain layer,
allowing for easy mocking in tests.
"""
