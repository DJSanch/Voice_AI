from __future__ import annotations

from typing import Optional

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover - optional dependency
    sr = None


def wait_for_wake_word() -> Optional[str]:
    """Wait for the wake word 'hey Astra' or fall back to typed input."""
    print("Say 'Astra' or 'hey Astra' to start. Type 'quit' to exit.")

    if sr is None:
        text = input("Command: ").strip()
        if not text:
            return None
        if text.lower() in {"quit", "exit"}:
            return None
        return text

    recognizer = sr.Recognizer()
    try:
        microphone = sr.Microphone(device_index=0)
    except Exception:
        try:
            microphone = sr.Microphone()
        except Exception:
            text = input("Command: ").strip()
            if not text:
                return None
            if text.lower() in {"quit", "exit"}:
                return None
            return text

    while True:
        try:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
                print("Listening for wake word...")
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except Exception:
            continue

        try:
            text = recognizer.recognize_google(audio).strip()
        except Exception:
            continue

        lowered = text.lower()
        if lowered in {"quit", "exit"}:
            return None
        if "astra" in lowered:
            print("Wake word detected.")
            return "astra"
        print(f"Heard: {text}")
