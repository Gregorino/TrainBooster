from pydub import AudioSegment
from pydub.playback import play
import os

def boost():
	audio_path = os.path.join(os.path.dirname(__file__), "audio.mp3")
	audio = AudioSegment.from_mp3(audio_path)
	play(audio)
