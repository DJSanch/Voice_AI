import urllib.request
import json
import subprocess


class StartupCheck:

    def __init__(self, model="llama3.2:3b"):
        self.model = model


    def check_ollama(self):

        try:
            url = "http://localhost:11434/api/tags"

            with urllib.request.urlopen(
                url,
                timeout=5
            ) as response:

                data = json.loads(
                    response.read().decode()
                )

            models = [
                model["name"]
                for model in data.get("models", [])
            ]

            if self.model in models:
                return "✓ Ollama connected"

            return f"⚠ Ollama running but {self.model} not found"


        except Exception:

            return "✗ Ollama not running"



    def check_microphone(self):

        try:
            import speech_recognition as sr

            sr.Microphone()

            return "✓ Microphone ready"

        except Exception:

            return "✗ Microphone unavailable"



    def run(self):

        print("\n--- Astra Startup Check ---")

        checks = [
            self.check_ollama(),
            self.check_microphone()
        ]

        for check in checks:
            print(check)

        print("---------------------------\n")