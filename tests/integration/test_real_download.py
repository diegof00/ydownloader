"""Exercise real yt-dlp and FFmpeg against locally generated media over HTTP."""

import json
import subprocess

import pytest

from src.domain.errors import CancelledException, DownloadError
from src.domain.models import DownloadFormat
from src.infra.ytdlp_adapter import YtdlpAdapter


def probe(path):
    return json.loads(
        subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=15,
        ).stdout
    )


@pytest.mark.parametrize(
    "format, suffix", [(DownloadFormat.AUDIO, ".mp3"), (DownloadFormat.VIDEO, ".mp4")]
)
def test_download_and_convert_real_media(media_server, tmp_path, format, suffix):
    progress = []
    adapter = YtdlpAdapter()
    result = adapter.download(f"{media_server}/sample.webm", tmp_path, format, progress.append)
    assert result.is_file()
    assert result.suffix == suffix
    metadata = probe(result)
    types = {stream["codec_type"] for stream in metadata["streams"]}
    assert types == ({"audio"} if format == DownloadFormat.AUDIO else {"audio", "video"})
    if format == DownloadFormat.AUDIO:
        assert metadata["streams"][0]["codec_name"] == "mp3"
    else:
        assert "mp4" in metadata["format"]["format_name"]
    assert any(update["status"] == "processing" for update in progress)
    assert not list(tmp_path.glob(".ydownloader-*"))
    second = adapter.download(f"{media_server}/sample.webm", tmp_path, format, lambda _: None)
    assert second != result
    assert result.is_file() and second.is_file()


def test_cancel_real_download_and_retry(media_server, tmp_path):
    unrelated = tmp_path / "other.part"
    unrelated.write_bytes(b"preserve")
    adapter = YtdlpAdapter()

    def cancel_on_progress(update):
        adapter.cancel()

    with pytest.raises(CancelledException):
        adapter.download(
            f"{media_server}/sample.webm", tmp_path, DownloadFormat.VIDEO, cancel_on_progress
        )
    assert list(tmp_path.iterdir()) == [unrelated]
    adapter.prepare()
    assert adapter.download(
        f"{media_server}/sample.webm", tmp_path, DownloadFormat.AUDIO, lambda _: None
    ).is_file()


def test_http_error_cleans_workspace(media_server, tmp_path):
    with pytest.raises(DownloadError):
        YtdlpAdapter().download(
            f"{media_server}/missing.webm", tmp_path, DownloadFormat.VIDEO, lambda _: None
        )
    assert not list(tmp_path.iterdir())


def test_cancel_at_postprocessing_boundary(media_server, tmp_path):
    adapter = YtdlpAdapter()

    def cancel_when_processing(update):
        if update["status"] == "processing":
            adapter.cancel()

    with pytest.raises(CancelledException):
        adapter.download(
            f"{media_server}/sample.webm", tmp_path, DownloadFormat.AUDIO, cancel_when_processing
        )
    assert not list(tmp_path.iterdir())
