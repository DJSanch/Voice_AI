from __future__ import annotations

from typing import Optional

from services.dashboard import update_dashboard_state

try:
    import speech_recognition as sr
except ImportError:
    sr = None


def wait_for_wake_word(alarm_active=False) -> Optional[str]:
    """Wait for the wake phrases 'Astra' or 'Good morning'."""

    print("Say 'Astra' or 'Good morning'. Type 'quit' to exit.")

    # Keyboard fallback
    if sr is None:
        text = input("Command: ").strip()

        if not text:
            return None

        if text.lower() in {"quit", "exit"}:
            return None

        return text.lower()

    recognizer = sr.Recognizer()

    # Faster recognition
    recognizer.pause_threshold = 0.5
    recognizer.non_speaking_duration = 0.4
    recognizer.phrase_threshold = 0.3
    recognizer.dynamic_energy_threshold = True

    # Microphone
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

            return text.lower()

    # Calibrate once
    with microphone as source:
        print("Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(
            source,
            duration=0.2
        )

    # Listen forever
    print("Listening for wake word...", flush=True)

    while True:

        try:
            with microphone as source:

                audio = recognizer.listen(
                    source,
                    timeout=2,
                    phrase_time_limit=5
                )

        except Exception:
            continue

        try:
            text = recognizer.recognize_google(audio).strip()

        except Exception:
            continue

        lowered = text.lower()

        if lowered in {"quit", "exit"}:
            update_dashboard_state(
                status="idle",
                mode="sleep",
                activity="Voice session ended",
            )
            return None

        if "good morning" in lowered:
            print("Morning briefing wake detected.")
            update_dashboard_state(
                status="active",
                mode="briefing",
                activity="Wake word detected: good morning",
                last_command=text,
            )
            return "good morning"

        if "astra" in lowered:
            print("Wake word detected.")
            update_dashboard_state(
                status="active",
                mode="conversation",
                activity="Wake word detected: Astra",
                last_command=text,
            )
            return "astra"
        
        if alarm_active and (
            "im awake" in lowered
            or "i'm awake" in lowered
        ):
            print("Alarm dismissal detected.")
            return "im awake"

        update_dashboard_state(
            status="listening",
            mode="wake",
            activity="Heard a voice cue",
            last_command=text,
        )
        print(f"Heard: {text}")