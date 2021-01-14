import playsound
import os

def boost():
	audio_path = os.path.join(os.path.dirname(__file__), "audio.mp3")
	playsound.playsound(audio_path,0)
