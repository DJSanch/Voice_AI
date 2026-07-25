import json
import urllib.request
from typing import Optional

from speech import SpeechController
from tts import TextToSpeech
from tools.network import NetworkTools
from tools.system import SystemTools
from wakeword import wait_for_wake_word


class VoiceAssistant:
    def __init__(self, name: str = "Astra") -> None:
        self.name = name
        self.speech = SpeechController()
        self.tts = TextToSpeech()
        self.system_tools = SystemTools()
        self.network_tools = NetworkTools()

    def _call_ollama(self, prompt: str) -> str:
        payload = {
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
        }
        request = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("response", "").strip()
        except Exception:
            return ""

    def handle_command(self, command: str) -> str:
        text = command.strip()
        if not text:
            return "I didn't catch that. Please try again."

        text = text.replace("\n", " ").strip()
        if text.lower().startswith("the"):
            text = text[4:].strip()

        lowered = text.lower()
        if not lowered:
            return "I didn't catch that. Please try again."
        normalized = lowered.replace(".", "").replace(",", "").strip()
        if normalized in {"hello", "hi", "hey", "hey there", "helo", "hullo", "hallo"}:
            return f"Hello! I'm {self.name}. How can I help you today?"
        if "hello" in normalized or "hi" in normalized:
            return f"Hello! I'm {self.name}. How can I help you today?"
        if "time" in lowered:
            return f"The current time is {self.system_tools.get_current_time()}."
        if "weather" in lowered:
            city = None
            if "in" in lowered:
                parts = lowered.split("in")
                if len(parts) > 1:
                    city = parts[-1].strip().split()[0].title()
            return self.network_tools.get_weather(city)

        prompt = (
            "You are a helpful voice assistant. Keep your answer short and conversational.\n"
            f"User: {text}\nAssistant:"
        )
        reply = self._call_ollama(prompt)
        if reply:
            return reply

        return "I can help with simple commands. Try saying hello or time."

    def run(self) -> None:
        while True:
            wake_word = wait_for_wake_word()
            if wake_word is None:
                break
            if wake_word:
                self.tts.speak("I'm listening.")
                print("Please say your command now...")
                command = self.speech.listen(timeout=8, phrase_time_limit=8)
                response = self.handle_command(command)
                self.tts.speak(response)
                print("Say 'hey Astra' again when you want another command.")
