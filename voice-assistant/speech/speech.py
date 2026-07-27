from __future__ import annotations

import os
import wave
from pathlib import Path
from typing import Optional

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover - optional dependency
    sr = None

try:
    import whisper
except ImportError:  # pragma: no cover - optional dependency
    whisper = None


class SpeechController:
    def __init__(self) -> None:
        self.recognizer: Optional[object] = None
        self.microphone: Optional[object] = None
        self.fallback_to_text = False
        self.model = None
        self._microphone_ready = False
        self.last_error: Optional[str] = None
        if sr is not None:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone(device_index=0)
                self._microphone_ready = True
            except Exception as exc:
                self.last_error = str(exc)
                try:
                    self.recognizer = sr.Recognizer()
                    self.microphone = sr.Microphone()
                    self._microphone_ready = True
                except Exception as exc2:
                    self.last_error = str(exc2)
                    self.fallback_to_text = True

        if whisper is not None:
            try:
                self.model = whisper.load_model("base")
            except Exception as exc:
                self.last_error = str(exc)
                self.model = None

    def _save_audio(self, audio_data: object, path: str) -> None:
        with wave.open(path, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_data.get_wav_data())

    def _normalize_command(self, text: str) -> str:
        cleaned = text.lower().strip()
        if not cleaned:
            return ""
        cleaned = cleaned.replace("'", "").replace(".", "").replace(",", "")
        cleaned = " ".join(cleaned.split())
        if cleaned.startswith("what time") or cleaned.startswith("what's the time"):
            return "time"
        if cleaned in {"time", "the time", "what time is it", "what time is it now"}:
            return "time"
        if cleaned in {"weather", "what weather", "what's the weather"}:
            return "weather"
        return cleaned

    def _dataset_hint(self, text: str) -> str:
        normalized = self._normalize_command(text)
        if normalized == "time":
            dataset_dir = Path(__file__).resolve().parent / "dataset" / "time"
            if dataset_dir.exists() and any(dataset_dir.glob("*.wav")):
                return "time"
        return normalized

    def listen(self, timeout: int = 20, phrase_time_limit: int = 30) -> str:
        if sr is None or self.recognizer is None or self.microphone is None:
            self.fallback_to_text = True

        if self.fallback_to_text:
            print("Microphone is unavailable. Please type your command instead.")
            if self.last_error:
                print(f"Reason: {self.last_error}")
            return input("You: ").strip()

        for attempt in range(2):
            try:
                with self.microphone as source:  # type: ignore[union-attr]
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    audio = self.recognizer.listen(source, timeout=max(timeout, 20), phrase_time_limit=max(phrase_time_limit, 30))
                break
            except Exception as exc:
                self.last_error = str(exc)
                if attempt == 1:
                    self.fallback_to_text = True
                    print("Microphone is unavailable. Please type your command instead.")
                    print(f"Reason: {self.last_error}")
                    return input("You: ").strip()
                print("Listening attempt failed. Retrying...")

        temp_path = "temp_audio.wav"
        try:
            self._save_audio(audio, temp_path)
            if self.model is not None:
                result = self.model.transcribe(temp_path, fp16=False, language="en")
                os.remove(temp_path)
                text = result.get("text", "").strip()
                print(f"Whisper transcription: {text!r}")
                if text:
                    normalized = self._dataset_hint(text)
                    print(f"Normalized command: {normalized!r}")
                    return normalized
            else:
                os.remove(temp_path)
        except Exception as exc:
            self.last_error = str(exc)
            print(f"Whisper error: {exc}")

        print("Trying Google transcription fallback...")
        try:
            fallback_text = self.recognizer.recognize_google(audio)
            print(f"Google fallback transcription: {fallback_text!r}")
            normalized = self._dataset_hint(fallback_text)
            print(f"Normalized command: {normalized!r}")
            return normalized
        except Exception as exc:
            self.last_error = str(exc)
            print(f"Fallback recognition error: {exc}")
            return ""
