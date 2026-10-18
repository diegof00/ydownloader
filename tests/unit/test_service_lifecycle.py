from pathlib import Path
from threading import Barrier, Event, Thread
from unittest.mock import Mock

import pytest

from src.domain.download_service import DownloadService
from src.domain.errors import CancelledException, DownloadError
from src.domain.models import DownloadFormat, DownloadStatus
from src.infra.ytdlp_adapter import YtdlpAdapter


def make_service(downloader=None, history=None):
    validator = Mock()
    validator.validate.return_value = Mock(is_valid=True)
    fs = Mock()
    fs.can_write.return_value = True
    adapter = downloader if downloader is not None else Mock()
    if isinstance(adapter, Mock):
        adapter.download.return_value = Path("/output/final.mp4")
    return DownloadService(validator, adapter, fs, history), validator, adapter


def start(service, **kwargs):
    return service.start_download(
        " https://example.com/video ",
        Path("/output"),
        DownloadFormat.VIDEO,
        kwargs.get("on_progress", Mock()),
        kwargs.get("on_complete", Mock()),
        kwargs.get("on_error", Mock()),
    )


def join(service):
    service._download_thread.join(5)
    assert not service._download_thread.is_alive()


def test_success_records_final_path_and_title():
    history = Mock()
    service, _, adapter = make_service(history=history)

    def download(**kwargs):
        kwargs["on_progress"]({"percent": 50, "status": "downloading", "title": "Title"})
        return Path("/output/final.mp4")

    adapter.download.side_effect = download
    complete, error = Mock(), Mock()
    job = start(service, on_complete=complete, on_error=error)
    join(service)
    assert job.status == DownloadStatus.COMPLETED
    assert job.url == "https://example.com/video"
    assert job.title == "Title"
    assert Path(history.add.call_args.args[0].output_path) == Path("/output/final.mp4")
    complete.assert_called_once_with(job)
    error.assert_not_called()
    assert not service.is_running()


@pytest.mark.parametrize(
    "exception, status",
    [
        (CancelledException(), DownloadStatus.CANCELLED),
        (DownloadError("internal", "Mensaje de error"), DownloadStatus.ERROR),
    ],
)
def test_failure_does_not_enter_history(exception, status):
    history = Mock()
    service, _, adapter = make_service(history=history)
    adapter.download.side_effect = exception
    complete, error = Mock(), Mock()
    job = start(service, on_complete=complete, on_error=error)
    join(service)
    assert job.status == status
    history.add.assert_not_called()
    if status == DownloadStatus.ERROR:
        error.assert_called_once_with("Mensaje de error")
        complete.assert_not_called()
    else:
        complete.assert_called_once_with(job)
        error.assert_not_called()


def test_simultaneous_starts_reserve_only_one_worker():
    service, validator, adapter = make_service()
    barrier, release = Barrier(2), Event()
    validator.validate.side_effect = lambda _: (barrier.wait(5), Mock(is_valid=True))[1]
    adapter.download.side_effect = lambda **_: (release.wait(5), Path("/output/final.mp4"))[1]
    results = []
    callers = [Thread(target=lambda: results.append(start(service))) for _ in range(2)]
    try:
        for thread in callers:
            thread.start()
        for thread in callers:
            thread.join(5)
            assert not thread.is_alive()
        assert sum(job is not None for job in results) == 1
        adapter.prepare.assert_called_once()
    finally:
        release.set()
        join(service)


def test_cancel_before_adapter_starts_is_not_lost(monkeypatch):
    import yt_dlp

    adapter = YtdlpAdapter()
    factory = Mock()
    monkeypatch.setattr(yt_dlp, "YoutubeDL", factory)
    service = DownloadService(Mock(), adapter, Mock())
    service._validator.validate.return_value = Mock(is_valid=True)

    def cancel(*_):
        service.cancel_download(service.get_current_download().id)

    job = start(service, on_progress=cancel)
    join(service)
    assert job.status == DownloadStatus.CANCELLED
    factory.assert_not_called()


def test_worker_remains_reserved_until_history_finishes():
    entered, release = Event(), Event()
    history = Mock()

    def save(_):
        entered.set()
        assert release.wait(5)

    history.add.side_effect = save
    service, _, _ = make_service(history=history)
    try:
        first = start(service)
        assert entered.wait(5)
        assert first.status == DownloadStatus.COMPLETED
        assert start(service) is None
    finally:
        release.set()
        join(service)
