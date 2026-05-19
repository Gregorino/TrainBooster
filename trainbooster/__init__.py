import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)

import os
import subprocess
from threading import Thread, Event
from tempfile import NamedTemporaryFile
from pydub import AudioSegment


def _load_audio_silently(path):
    """Load audio while suppressing ffmpeg stderr output."""
    old_stderr = os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, 2)
    try:
        audio = AudioSegment.from_mp3(path)
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)
        os.close(devnull)
    return audio


class BoosterContext:
    def __init__(self):
        self._stop_event = Event()
        self._thread = None

    def start(self):
        if self._thread is None or not self._thread.is_alive():
            self._stop_event.clear()
            self._thread = Thread(target=self._play_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3)

    def _play_loop(self):
        audio_path = os.path.join(os.path.dirname(__file__), "audio.mp3")
        audio = _load_audio_silently(audio_path)

        with NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name

        old_stderr = os.dup(2)
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 2)
        try:
            audio.export(tmp_path, "wav")
        finally:
            os.dup2(old_stderr, 2)
            os.close(old_stderr)
            os.close(devnull)

        try:
            while not self._stop_event.is_set():
                proc = subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                while proc.poll() is None:
                    if self._stop_event.wait(timeout=0.1):
                        proc.terminate()
                        proc.wait()
                        break
        finally:
            os.unlink(tmp_path)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False


def boost():
    """Play boost audio continuously; use as a context manager to stop on exit."""
    return BoosterContext()


booster = boost
