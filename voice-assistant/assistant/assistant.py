import subprocess

from .router import CommandRouter

from speech import SpeechController
from speech import TextToSpeech
from speech.wakeword import wait_for_wake_word

from services.weather import WeatherService
from services.llm import LLMService
from services.spotify import SpotifyService
from services.timer import TimerService
from tools.system import SystemTools


class VoiceAssistant:

    def __init__(self, name: str = "Astra") -> None:
        self.name = name

        self.speech = SpeechController()
        self.tts = TextToSpeech()

        self.system_tools = SystemTools()

        # Services
        self.weather = WeatherService()
        self.llm = LLMService()
        self.spotify = SpotifyService()
        self.timer = TimerService()

        # Router
        self.router = CommandRouter(
            weather=self.weather,
            spotify=self.spotify,
            llm=self.llm,
            system_tools=self.system_tools,
            timer=self.timer
        )


    def _open_weather_app(self) -> None:
        try:
            subprocess.run(
                ["open", "-a", "Weather"],
                check=False
            )
        except Exception:
            pass


    def handle_command(self, command: str) -> str:
        if not command.strip():
            return "I didn't catch that. Please try again."

        return self.router.handle(command)


    def run(self) -> None:
        while True:

            wake_word = wait_for_wake_word()

            if wake_word is None:
                break

            if wake_word:

                self.tts.speak(
                    "Hello master Daniel, how can I help?"
                )

                while True:
                    print("Listening...")

                    command = self.speech.listen(
                        timeout=15,
                        phrase_time_limit=12
                    )

                    if not command:
                        print("No command detected. Sleeping...")
                        break

                    response = self.handle_command(command)

                    self.tts.speak(response)

                    print("Waiting for next command...")