"""Optional real Tk GUI flow; run with YDOWNLOADER_TEST_GUI=1 on a display."""

import os
import time
from pathlib import Path
from threading import Event
from unittest.mock import Mock

import pytest

from src.domain.errors import CancelledException
from src.domain.models import DownloadFormat, DownloadStatus
from src.infra.config_store import ConfigStore
from src.infra.history_store import HistoryStore

pytestmark = pytest.mark.skipif(
    os.environ.get("YDOWNLOADER_TEST_GUI") != "1", reason="GUI tests are opt-in"
)


def test_gui_download_error_history_and_preferences(tmp_path, monkeypatch, media_server):
    from src.ui import main_window

    config = ConfigStore(tmp_path / "config.json")
    config.set_last_output_folder(tmp_path)
    config.mark_disclaimer_shown()
    history = HistoryStore(tmp_path / "history.json")
    errors = Mock()
    monkeypatch.setattr(main_window, "ConfigStore", lambda: config)
    monkeypatch.setattr(main_window, "HistoryStore", lambda: history)
    monkeypatch.setattr(main_window, "show_error", errors)
    app = main_window.MainWindow()
    callback_errors = []
    app.report_callback_exception = lambda *error: callback_errors.append(error)

    def wait_for_idle():
        deadline = time.monotonic() + 20
        while app._download_button.is_downloading() and time.monotonic() < deadline:
            app.update()
            time.sleep(0.01)
        assert not app._download_button.is_downloading()
        assert not callback_errors

    destroyed = False
    try:
        app.update()
        assert app.winfo_width() >= 500
        app._url_input.set_url("invalid")
        app._download_button._button.invoke()
        wait_for_idle()
        errors.assert_called_once()
        errors.reset_mock()

        for format in (DownloadFormat.AUDIO, DownloadFormat.VIDEO):
            app._format_selector._on_select("Audio" if format == DownloadFormat.AUDIO else "Video")
            app._url_input.set_url(f"{media_server}/sample.webm")
            app._download_button._button.invoke()
            assert app._download_button.is_downloading()
            assert app._url_input._entry.cget("state") == "disabled"
            wait_for_idle()
            assert app._progress_bar.get_status() == DownloadStatus.COMPLETED
            assert app._url_input._entry.cget("state") == "normal"
            assert ConfigStore(tmp_path / "config.json").get_default_format() == format
            entries = HistoryStore(tmp_path / "history.json").get_entries()
            assert Path(entries[0].output_path).is_file()
            assert entries[0].format == format.value
        errors.assert_not_called()
        assert len(app._history_panel._entries) == 2
        app._clear_history()
        assert not HistoryStore(tmp_path / "history.json").get_entries()
        app.update()

        # Closing an active job waits for the worker to finish cleanup.
        entered, release = Event(), Event()
        adapter = Mock()

        def downloading(**_):
            entered.set()
            release.wait(5)
            raise CancelledException()

        adapter.download.side_effect = downloading
        adapter.cancel.side_effect = release.set
        app._download_service._downloader = adapter
        app._download_button._button.invoke()
        assert entered.wait(5)
        monkeypatch.setattr(main_window.messagebox, "askyesno", lambda *_: False)
        app._on_close()
        assert not app._closing
        assert app._download_service.is_running()
        monkeypatch.setattr(main_window.messagebox, "askyesno", lambda *_: True)
        destroy = Mock(wraps=app.destroy)
        monkeypatch.setattr(app, "destroy", destroy)
        app._on_close()
        deadline = time.monotonic() + 5
        while not destroy.called and time.monotonic() < deadline:
            app.update()
            time.sleep(0.01)
        destroyed = destroy.called
        assert destroyed
        assert not app._download_service.is_running()
    finally:
        thread = app._download_service._download_thread
        if thread and thread.is_alive():
            app._cancel_download()
            thread.join(20)
        if not destroyed:
            app.destroy()
