from __future__ import annotations

import os
import wave
from pathlib import Path
from typing import List

import pyaudio


class VoiceDatasetCollector:
    def __init__(self, output_dir: str = "dataset") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def record_sample(self, label: str, duration: int = 3, sample_rate: int = 16000) -> str:
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            frames_per_buffer=1024,
        )

        print(f"Recording {label} for {duration} seconds...")
        frames = []
        for _ in range(0, int(sample_rate / 1024 * duration)):
            data = stream.read(1024)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        label_dir = self.output_dir / label
        label_dir.mkdir(parents=True, exist_ok=True)

        filename = label_dir / f"{len(list(label_dir.glob('*.wav'))):03d}.wav"
        with wave.open(str(filename), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b"".join(frames))

        print(f"Saved: {filename}")
        return str(filename)

    def list_samples(self) -> List[str]:
        return [str(path) for path in sorted(self.output_dir.rglob("*.wav"))]
