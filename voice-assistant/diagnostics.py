from __future__ import annotations

import os
import platform
import subprocess
import sys

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover - optional dependency
    sr = None


class AudioDiagnostics:
    def run(self) -> None:
        print("=== Audio Diagnostics ===")
        print(f"Python: {sys.executable}")
        print(f"Platform: {platform.platform()}")

        if sr is None:
            print("speech_recognition is not installed")
            return

        print("Checking microphone devices...")
        try:
            devices = sr.Microphone.list_microphone_names()
            if not devices:
                print("No microphone devices found.")
                return
            for idx, name in enumerate(devices):
                print(f"[{idx}] {name}")
        except Exception as exc:
            print(f"Unable to list microphones: {exc}")

        print("\nChecking for macOS permissions...")
        if platform.system() == "Darwin":
            try:
                result = subprocess.run(
                    ["tcc", "-E", "-x", "c", "-"],
                    input="#include <AudioToolbox/AudioToolbox.h>\nint main(){return 0;}",
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    print("macOS audio framework is available.")
                else:
                    print("macOS audio framework check failed.")
            except Exception as exc:
                print(f"macOS audio framework check error: {exc}")

        print("\nSuggested checks:")
        print("- Open System Settings > Privacy & Security > Microphone")
        print("- Make sure Terminal/Python has microphone access")
        print("- Close apps like Teams/Zoom/Discord if they are using the mic")
        print("- Reconnect USB or Bluetooth audio devices if needed")
