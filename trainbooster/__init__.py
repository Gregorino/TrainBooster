import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)

import os
import subprocess
from contextlib import contextmanager
from threading import Thread, Event, Lock
from tempfile import NamedTemporaryFile
from pydub import AudioSegment
from pydub.playback import play  # kept for boost() / backward compat

_stderr_lock = Lock()


@contextmanager
def _quiet_stderr():
    with _stderr_lock:
        old = os.dup(2)
        null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(null, 2)
        try:
            yield
        finally:
            os.dup2(old, 2)
            os.close(old)
            os.close(null)


class BoosterContext:
    def __init__(self):
        self.playing = False
        self.playback_thread = None
        self._stop_event = Event()

    def start(self):
        if not self.playing:
            self.playing = True
            self._stop_event.clear()
            self.playback_thread = Thread(target=self._play_loop, daemon=True)
            self.playback_thread.start()

    def stop(self):
        self.playing = False
        self._stop_event.set()
        if self.playback_thread:
            self.playback_thread.join(timeout=3)

    def _play_loop(self):
        audio_path = os.path.join(os.path.dirname(__file__), "audio.mp3")

        with _quiet_stderr():
            audio = AudioSegment.from_mp3(audio_path)

        with NamedTemporaryFile(suffix=".wav", delete=False) as f:
            tmp_path = f.name
        with _quiet_stderr():
            audio.export(tmp_path, "wav")

        try:
            while self.playing:
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
    """Play boost audio once in a non-blocking way."""
    audio_path = os.path.join(os.path.dirname(__file__), "audio.mp3")
    with _quiet_stderr():
        audio = AudioSegment.from_mp3(audio_path)
    thread = Thread(target=play, args=(audio,), daemon=True)
    thread.start()


def booster():
    """Context manager for playing boost audio continuously."""
    return BoosterContext()
