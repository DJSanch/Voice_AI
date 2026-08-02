from __future__ import annotations

import os
import platform
import subprocess
import sys
import shutil

try:
    import speech_recognition as sr
except ImportError:
    sr = None


class AudioDiagnostics:

    def run(self) -> None:

        print("=== Astra Audio Diagnostics ===\n")

        self.system_info()

        self.check_speech_recognition()

        self.list_microphones()

        self.check_macos_audio()

        self.check_audio_tools()

        self.summary()



    # -----------------------------
    # System Information
    # -----------------------------

    def system_info(self):

        print("System Information")

        print(
            f"Python: {sys.executable}"
        )

        print(
            f"Platform: {platform.platform()}"
        )

        print(
            f"Architecture: {platform.machine()}"
        )

        print()



    # -----------------------------
    # Speech Recognition
    # -----------------------------

    def check_speech_recognition(self):

        print("Speech Recognition")

        if sr is None:

            print(
                "❌ speech_recognition not installed"
            )

        else:

            print(
                "✓ speech_recognition available"
            )


        print()



    # -----------------------------
    # Microphones
    # -----------------------------

    def list_microphones(self):

        print("Microphone Devices")

        if sr is None:
            return


        try:

            devices = (
                sr.Microphone
                .list_microphone_names()
            )


            if not devices:

                print(
                    "❌ No microphones detected"
                )

                return


            for index, device in enumerate(devices):

                print(
                    f"[{index}] {device}"
                )


        except Exception as e:

            print(
                f"Microphone error: {e}"
            )


        print()



    # -----------------------------
    # macOS Audio
    # -----------------------------

    def check_macos_audio(self):

        print("macOS Audio Devices")


        if platform.system() != "Darwin":

            print(
                "Not macOS"
            )

            return


        try:

            result = subprocess.run(
                [
                    "system_profiler",
                    "SPAUDIODataType"
                ],

                capture_output=True,

                text=True
            )


            if result.stdout:

                print(
                    result.stdout[:2000]
                )

            else:

                print(
                    "No audio information found"
                )


        except Exception as e:

            print(
                f"Audio system error: {e}"
            )


        print()



    # -----------------------------
    # External Tools
    # -----------------------------

    def check_audio_tools(self):

        print("Audio Tools")


        tools = [
            "ffmpeg",
            "sox",
            "rec"
        ]


        for tool in tools:

            if shutil.which(tool):

                print(
                    f"✓ {tool} installed"
                )

            else:

                print(
                    f"- {tool} unavailable"
                )


        print()



    # -----------------------------
    # Final Summary
    # -----------------------------

    def summary(self):

        print(
            "Suggested fixes:"
        )

        print(
            "- Check System Settings > Privacy & Security > Microphone"
        )

        print(
            "- Allow Terminal/Python microphone access"
        )

        print(
            "- Close apps using microphone"
        )

        print(
            "- Restart CoreAudio if needed:"
        )

        print(
            "  sudo killall coreaudiod"
        )