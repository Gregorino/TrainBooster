import os
import time
import pytest
from unittest.mock import patch, MagicMock


def test_public_api_exists():
    import trainbooster
    assert callable(trainbooster.boost)
    assert callable(trainbooster.booster)
    assert trainbooster.BoosterContext


def test_audio_file_bundled():
    import trainbooster
    audio_path = os.path.join(os.path.dirname(trainbooster.__file__), "audio.mp3")
    assert os.path.isfile(audio_path), "audio.mp3 must be bundled with the package"


@pytest.fixture
def mocked_audio():
    """Patch pydub and subprocess so tests never touch real audio hardware."""
    mock_proc = MagicMock()
    mock_proc.poll.return_value = None  # simulate process still running until stop()

    with patch("trainbooster.AudioSegment.from_mp3") as mock_load, \
         patch("trainbooster.play") as mock_play, \
         patch("trainbooster.subprocess.Popen", return_value=mock_proc):
        mock_load.return_value = MagicMock()
        yield mock_load, mock_play


def test_booster_context_starts_and_stops(mocked_audio):
    from trainbooster import BoosterContext

    ctx = BoosterContext()
    assert not ctx.playing
    assert ctx.playback_thread is None

    ctx.start()
    assert ctx.playing
    assert ctx.playback_thread is not None
    assert ctx.playback_thread.is_alive()

    ctx.stop()
    assert not ctx.playing


def test_booster_context_start_is_idempotent(mocked_audio):
    from trainbooster import BoosterContext

    ctx = BoosterContext()
    ctx.start()
    thread_before = ctx.playback_thread
    ctx.start()  # second call should be a no-op
    assert ctx.playback_thread is thread_before
    ctx.stop()


def test_booster_context_manager(mocked_audio):
    from trainbooster import booster

    with booster():
        pass  # should start and stop cleanly without exceptions


def test_booster_context_manager_stops_on_exception(mocked_audio):
    from trainbooster import booster

    with pytest.raises(RuntimeError):
        with booster() as ctx:
            assert ctx.playing
            raise RuntimeError("simulated training error")

    # audio must stop even when an exception propagates
    assert not ctx.playing


def test_boost_is_non_blocking(mocked_audio):
    mock_load, mock_play = mocked_audio
    from trainbooster import boost

    boost()
    # boost() returns immediately; give the daemon thread a moment to run
    time.sleep(0.05)
    mock_play.assert_called_once()


def test_boost_uses_bundled_audio(mocked_audio):
    mock_load, _ = mocked_audio
    import trainbooster
    from trainbooster import boost

    boost()
    time.sleep(0.05)

    called_path = mock_load.call_args[0][0]
    expected_dir = os.path.dirname(trainbooster.__file__)
    assert called_path.startswith(expected_dir)
    assert called_path.endswith("audio.mp3")
