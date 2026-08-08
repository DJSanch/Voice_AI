from __future__ import annotations

import math
import os
import struct
import wave
from pathlib import Path
from typing import Optional
import threading

try:
    import speech_recognition as sr
except ImportError:
    sr = None

try:
    import whisper
except ImportError:
    whisper = None


class SpeechController:

    def __init__(self) -> None:

        self.recognizer: Optional[object] = None
        self.microphone: Optional[object] = None

        self.fallback_to_text = False
        self.model = None

        self._microphone_ready = False
        self.last_error: Optional[str] = None

        # Prevent repeated calibration
        self.calibrated = False
        self.mic_lock = threading.Lock()


        if sr is not None:

            try:

                self.recognizer = sr.Recognizer()

                # Voice assistant tuning
                self.recognizer.pause_threshold = 1.2
                self.recognizer.non_speaking_duration = 0.8
                self.recognizer.phrase_threshold = 0.3

                self.microphone = sr.Microphone(
                    device_index=0
                )

                self._microphone_ready = True


            except Exception as exc:

                self.last_error = str(exc)

                try:

                    self.recognizer = sr.Recognizer()

                    self.recognizer.pause_threshold = 1.2
                    self.recognizer.non_speaking_duration = 0.8
                    self.recognizer.phrase_threshold = 0.3

                    self.microphone = sr.Microphone()

                    self._microphone_ready = True


                except Exception as exc2:

                    self.last_error = str(exc2)
                    self.fallback_to_text = True


        if whisper is not None:

            try:

                self.model = whisper.load_model(
                    "base"
                )

            except Exception as exc:

                self.last_error = str(exc)
                self.model = None



    def _save_audio(
        self,
        audio_data: object,
        path: str
    ) -> None:

        with wave.open(path, "wb") as wav_file:

            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)

            wav_file.writeframes(
                audio_data.get_wav_data()
            )


    def _measure_voice_strength(
        self,
        audio_data: object
    ) -> float:
        raw = audio_data.get_raw_data(convert_rate=16000, convert_width=2)
        if not raw:
            return 0.0

        sample_count = len(raw) // 2
        if sample_count == 0:
            return 0.0

        samples = struct.unpack(f"<{sample_count}h", raw)
        rms = math.sqrt(sum(sample * sample for sample in samples) / sample_count)
        return min(1.0, rms / 16000.0)


    def _normalize_command(
        self,
        text: str
    ) -> str:

        cleaned = text.lower().strip()

        if not cleaned:
            return ""

        cleaned = (
            cleaned
            .replace("'", "")
            .replace(".", "")
            .replace(",", "")
        )

        cleaned = " ".join(
            cleaned.split()
        )


        if (
            cleaned.startswith("what time")
            or cleaned.startswith("whats the time")
        ):
            return "time"


        if cleaned in {
            "time",
            "the time",
            "what time is it",
            "what time is it now"
        }:
            return "time"


        if cleaned in {
            "weather",
            "what weather",
            "whats the weather"
        }:
            return "weather"


        return cleaned



    def _dataset_hint(
        self,
        text: str
    ) -> str:

        normalized = self._normalize_command(text)

        if normalized == "time":

            dataset_dir = (
                Path(__file__)
                .resolve()
                .parent
                / "dataset"
                / "time"
            )

            if dataset_dir.exists() and any(
                dataset_dir.glob("*.wav")
            ):
                return "time"


        return normalized



    def listen(
        self,
        timeout=20,
        phrase_time_limit=60
    ):

        try:

            with self.microphone as source:

                if not self.calibrated:

                    self.recognizer.adjust_for_ambient_noise(
                        source,
                        duration=0.5
                    )

                    self.calibrated = True


                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            voice_strength = self._measure_voice_strength(audio)

            text = self.recognizer.recognize_google(
                audio
            )


            print(
                f"Google transcription: {text}"
            )

            normalized = self._normalize_command(text)

            return normalized


        except Exception as exc:

            print(
                f"Speech error: {exc}"
            )

            return ""
