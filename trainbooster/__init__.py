import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)

from pydub import AudioSegment
from pydub.playback import play
import os
from threading import Thread
from contextlib import contextmanager

class BoosterContext:
	def __init__(self):
		self.playing = False
		self.playback_thread = None
	
	def start(self):
		"""Start playing audio in a background thread"""
		if not self.playing:
			self.playing = True
			self.playback_thread = Thread(target=self._play_loop, daemon=True)
			self.playback_thread.start()
	
	def stop(self):
		"""Stop playing audio"""
		self.playing = False
		if self.playback_thread:
			self.playback_thread.join(timeout=5)
	
	def _play_loop(self):
		"""Play audio continuously until stopped"""
		audio_path = os.path.join(os.path.dirname(__file__), "audio.mp3")
		audio = AudioSegment.from_mp3(audio_path)
		
		while self.playing:
			play(audio)
	
	def __enter__(self):
		self.start()
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.stop()

@contextmanager
def booster():
	"""Context manager for playing boost audio continuously
	
	Usage:
		with booster():
			# Your training code here
			train_model()
	"""
	ctx = BoosterContext()
	ctx.start()
	try:
		yield ctx
	finally:
		ctx.stop()

def boost():
	"""Play boost audio once in a non-blocking way"""
	audio_path = os.path.join(os.path.dirname(__file__), "audio.mp3")
	audio = AudioSegment.from_mp3(audio_path)
	thread = Thread(target=play, args=(audio,), daemon=True)
	thread.start()
