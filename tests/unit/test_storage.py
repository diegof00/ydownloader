import pytest

from src.infra.config_store import ConfigStore
from src.infra.file_system import FileSystem
from src.infra.history_store import HistoryStore


@pytest.mark.parametrize("content", ["{", "null", "[]", "42"])
def test_invalid_json_structure_uses_defaults(tmp_path, content):
    path = tmp_path / "settings.json"
    path.write_text(content)
    assert ConfigStore(path).get_default_format().value == "video"
    assert HistoryStore(path).get_entries() == []


def test_unreadable_storage_uses_defaults(tmp_path):
    assert ConfigStore(tmp_path).should_show_disclaimer() is True
    assert HistoryStore(tmp_path).get_entries() == []


def test_permission_probe_preserves_existing_file(tmp_path):
    path = tmp_path / ".ydownloader_write_test"
    path.write_text("user data")
    assert FileSystem().can_write(tmp_path) is True
    assert path.read_text() == "user data"


def test_malformed_settings_fields_do_not_crash(tmp_path):
    import json

    path = tmp_path / "config.json"
    path.write_text(
        json.dumps({"last_output_folder": 42, "default_format": [], "show_disclaimer": "false"})
    )
    store = ConfigStore(path)
    assert store.get_last_output_folder() is None
    assert store.get_default_format().value == "video"
    assert store.should_show_disclaimer() is True


def test_history_keeps_valid_entries_and_enforces_limit(tmp_path):
    import json

    from src.domain.models import HistoryEntry

    path = tmp_path / "history.json"
    valid = HistoryEntry(
        "id", "title", "/output/a.mp4", "completed", "video", "2026-10-18T10:00:00"
    )
    path.write_text(json.dumps({"entries": [None, {"title": 42}] + [valid.to_dict()] * 8}))
    store = HistoryStore(path)
    assert len(store.get_entries()) == 5
    entries = store.get_entries()
    entries.clear()
    assert len(store.get_entries()) == 5


def test_history_concurrent_mutations_are_persisted(tmp_path):
    import json
    from concurrent.futures import ThreadPoolExecutor

    from src.domain.models import HistoryEntry

    path = tmp_path / "history.json"
    store = HistoryStore(path)

    def add(index):
        store.add(HistoryEntry(str(index), "title", "/output/a.mp4", "completed", "video", ""))

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(add, range(40)))
    assert len(json.loads(path.read_text())["entries"]) == 5
    assert HistoryStore(path).get_entries() == store.get_entries()
