from __future__ import annotations

import os
import re
import shutil
import subprocess

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class TextToSpeech:

    def __init__(self) -> None:

        self.engine = None

        if pyttsx3 is not None:
            self.engine = pyttsx3.init()



    def clean_text(self, text: str) -> str:

        def convert_mac(match):

            mac = match.group()

            parts = mac.split(":")

            return (
                "MAC address "
                + " ".join(parts)
            )


        # Convert MAC addresses into readable speech
        text = re.sub(
            r"\b([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b",
            convert_mac,
            text
        )


        # Convert IP addresses
        def convert_ip(match):

            ip = match.group()

            return (
                "IP address "
                + ip.replace(".", " point ")
            )


        text = re.sub(
            r"\b\d{1,3}(\.\d{1,3}){3}\b",
            convert_ip,
            text
        )


        # Replace underscores
        text = text.replace(
            "_",
            " "
        )


        return text



    def speak(
        self,
        text: str
    ) -> None:


        text = self.clean_text(
            text
        )


        if shutil.which("say"):

            subprocess.run(
                [
                    "say",
                    text
                ],
                check=False
            )

            return



        if self.engine is not None:

            self.engine.say(
                text
            )

            self.engine.runAndWait()

            return



        print(
            f"TTS: {text}"
        )



    def play_audio_file(
        self,
        path: str
    ) -> None:


        if not os.path.exists(path):

            print(
                f"Audio file not found: {path}"
            )

            return



        if shutil.which("afplay"):

            subprocess.run(
                [
                    "afplay",
                    path
                ],
                check=False
            )

            return



        print(
            f"Audio playback unavailable for: {path}"
        )