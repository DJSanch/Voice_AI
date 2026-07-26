from __future__ import annotations

import os
import shutil
import subprocess

try:
    import pyttsx3
except ImportError:  # pragma: no cover - optional dependency
    pyttsx3 = None


class TextToSpeech:
    def __init__(self) -> None:
        self.engine = None
        if pyttsx3 is not None:
            self.engine = pyttsx3.init()

    def speak(self, text: str) -> None:
        if shutil.which("say"):
            subprocess.run(["say", text], check=False)
            return
        if self.engine is not None:
            self.engine.say(text)
            self.engine.runAndWait()
            return
        print(f"TTS: {text}")

    def play_audio_file(self, path: str) -> None:
        if not os.path.exists(path):
            print(f"Audio file not found: {path}")
            return
        if shutil.which("afplay"):
            subprocess.run(["afplay", path], check=False)
            return
        print(f"Audio playback unavailable for: {path}")
