from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yt_dlp

from src.domain.errors import CancelledException, DownloadError
from src.domain.models import DownloadFormat
from src.infra.ytdlp_adapter import YtdlpAdapter


@pytest.fixture(autouse=True)
def ffmpeg_available(monkeypatch):
    # Unit tests mock yt-dlp; they must not depend on a system FFmpeg install.
    monkeypatch.setattr("src.infra.ytdlp_adapter.shutil.which", lambda name: f"/mock/{name}")


@pytest.mark.parametrize(
    "format, extension",
    [
        (DownloadFormat.AUDIO, "mp3"),
        (DownloadFormat.VIDEO, "mp4"),
    ],
)
def test_returns_postprocessed_file_without_overwriting(tmp_path, monkeypatch, format, extension):
    existing = tmp_path / f"Example.{extension}"
    existing.write_bytes(b"original")
    options = {}
    client = MagicMock()

    def factory(opts):
        options.update(opts)
        return client

    def extract(url, download):
        assert download is True
        workspace = Path(options["outtmpl"]).parent
        source = workspace / "Example.webm"
        source.write_bytes(b"source")
        options["progress_hooks"][0]({"status": "finished", "filename": str(source)})
        source.unlink()
        final = workspace / f"Example.{extension}"
        final.write_bytes(b"converted")
        options["post_hooks"][0](str(final))
        return {"title": "Example"}

    client.__enter__.return_value.extract_info.side_effect = extract
    monkeypatch.setattr(yt_dlp, "YoutubeDL", factory)
    result = YtdlpAdapter().download("https://example.com/video", tmp_path, format, lambda _: None)
    assert result == tmp_path / f"Example (1).{extension}"
    assert result.read_bytes() == b"converted"
    assert existing.read_bytes() == b"original"
    assert options["noplaylist"] is True
    assert not list(tmp_path.glob(".ydownloader-*"))


@pytest.mark.parametrize("wrapped", [False, True])
def test_cancel_preserves_unrelated_partial_files(tmp_path, monkeypatch, wrapped):
    unrelated = tmp_path / "other.part"
    unrelated.write_bytes(b"keep")
    adapter = YtdlpAdapter()
    client = MagicMock()

    def factory(options):
        def extract(*args, **kwargs):
            workspace = Path(options["outtmpl"]).parent
            (workspace / "current.part").write_bytes(b"partial")
            adapter.cancel()
            if wrapped:
                raise yt_dlp.utils.DownloadError("cancelled")
            options["progress_hooks"][0]({"status": "downloading"})

        client.__enter__.return_value.extract_info.side_effect = extract
        return client

    monkeypatch.setattr(yt_dlp, "YoutubeDL", factory)
    with pytest.raises(CancelledException):
        adapter.download(
            "https://example.com/video", tmp_path, DownloadFormat.VIDEO, lambda _: None
        )
    assert unrelated.read_bytes() == b"keep"
    assert list(tmp_path.iterdir()) == [unrelated]


def test_missing_final_file_is_error(tmp_path, monkeypatch):
    client = MagicMock()
    client.__enter__.return_value.extract_info.return_value = {"title": "Missing"}
    monkeypatch.setattr(yt_dlp, "YoutubeDL", lambda _: client)
    with pytest.raises(DownloadError):
        YtdlpAdapter().download(
            "https://example.com/video", tmp_path, DownloadFormat.AUDIO, lambda _: None
        )
    assert not list(tmp_path.iterdir())


def test_missing_ffmpeg_has_actionable_error(tmp_path, monkeypatch):
    monkeypatch.setattr("src.infra.ytdlp_adapter.shutil.which", lambda _: None)
    with pytest.raises(DownloadError, match="FFmpeg") as error:
        YtdlpAdapter().download(
            "https://example.com/video", tmp_path, DownloadFormat.AUDIO, lambda _: None
        )
    assert "FFmpeg" in error.value.user_message
    assert not list(tmp_path.iterdir())


def test_authentication_error_explains_real_cause(tmp_path, monkeypatch):
    client = MagicMock()
    client.__enter__.return_value.extract_info.side_effect = yt_dlp.utils.DownloadError(
        "Sign in to confirm you're not a bot"
    )
    monkeypatch.setattr(yt_dlp, "YoutubeDL", lambda _: client)
    with pytest.raises(DownloadError) as error:
        YtdlpAdapter().download(
            "https://example.com/video", tmp_path, DownloadFormat.VIDEO, lambda _: None
        )
    assert "autenticación" in error.value.user_message
    assert not list(tmp_path.iterdir())
