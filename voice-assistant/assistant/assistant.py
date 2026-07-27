from .router import CommandRouter
from speech import SpeechController
from speech import TextToSpeech
from speech.wakeword import wait_for_wake_word

from services.weather import WeatherService
from services.llm import LLMService
from services.spotify import SpotifyService
from services.timer import TimerService
from services.notes import NotesService
from services.news import NewsService
from services.briefing import BriefingService

from tools.system import SystemTools


class VoiceAssistant:

    def __init__(self, name: str = "Astra") -> None:
        self.name = name

        # Services
        self.speech = SpeechController()
        self.tts = TextToSpeech()

        self.system_tools = SystemTools()

        self.weather = WeatherService()
        self.llm = LLMService()
        self.spotify = SpotifyService()
        self.timer = TimerService()
        self.notes = NotesService()
        self.news = NewsService()

        self.briefing = BriefingService(
            weather=self.weather,
            news=self.news,
            notes=self.notes,
            system_tools=self.system_tools,
            tts=self.tts
        )


        # Router
        self.router = CommandRouter(
            weather=self.weather,
            spotify=self.spotify,
            llm=self.llm,
            system_tools=self.system_tools,
            timer=self.timer,
            notes=self.notes,
            news=self.news,
            briefing=self.briefing
        )


    def handle_command(self, command: str) -> str:

        if not command.strip():
            return "I didn't catch that. Please try again."

        return self.router.handle(command)


    def run(self) -> None:

        spotify_active = False


        while True:

            # Sleep mode - waiting for wake word
            wake_command = wait_for_wake_word()


            if wake_command is None:
                break


            # Morning briefing
            if wake_command == "good morning":

                self.briefing.get_briefing()

                print("Briefing complete.")

                continue



            # Normal wake
            self.tts.speak(
                "Hello master Daniel, how can I help?"
            )


            # Active listening mode
            while True:

                print("Listening...")

                command = self.speech.listen(
                    timeout=10,
                    phrase_time_limit=100
                )


                if not command:

                    if spotify_active:
                        print(
                            "Spotify active. Still listening..."
                        )
                        continue

                    else:
                        print(
                            "No active session. Returning to wake mode..."
                        )
                        break



                lowered = command.lower()


                # Spotify started
                if any(
                    word in lowered
                    for word in [
                        "play",
                        "spotify",
                        "music"
                    ]
                ):
                    spotify_active = True



                # Spotify stopped
                if any(
                    phrase in lowered
                    for phrase in [
                        "pause",
                        "pause music",
                        "pause spotify",
                        "stop",
                        "stop music",
                        "stop spotify"
                    ]
                ):
                    spotify_active = False



                response = self.handle_command(command)

                self.tts.speak(response)



                if spotify_active:

                    print(
                        "Spotify active. Waiting for next command..."
                    )

                else:

                    print(
                        "Command complete. Returning to wake mode..."
                    )

                    break