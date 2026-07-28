from .router import CommandRouter
from speech import SpeechController
from speech import TextToSpeech
from speech.wakeword import wait_for_wake_word
from services.mac_status import MacStatusService
from services.weather import WeatherService
from services.llm import LLMService
from services.spotify import SpotifyService
from services.timer import TimerService
from services.notes import NotesService
from services.news import NewsService
from services.briefing import BriefingService
from services.alarm import AlarmService
from tools.system import SystemTools


class VoiceAssistant:

    def __init__(self, name: str = "Astra") -> None:

        self.name = name
        # Speech
        self.speech = SpeechController()
        self.tts = TextToSpeech()
        self.music_mode = False

        # Tools
        self.system_tools = SystemTools()
        


        # Services
        self.weather = WeatherService()
        self.llm = LLMService()
        self.spotify = SpotifyService()
        self.timer = TimerService()
        self.notes = NotesService()
        self.news = NewsService()
        self.mac_status = MacStatusService()
        


        # Briefing
        self.briefing = BriefingService(
            weather=self.weather,
            news=self.news,
            notes=self.notes,
            system_tools=self.system_tools,
            tts=self.tts
        )
        

        # Alarm
        self.alarm = AlarmService(
            briefing=self.briefing,
            spotify=self.spotify,
            tts=self.tts,
            speech=self.speech
        )


        # Command Router
        self.router = CommandRouter(
            weather=self.weather,
            spotify=self.spotify,
            llm=self.llm,
            system_tools=self.system_tools,
            timer=self.timer,
            notes=self.notes,
            news=self.news,
            briefing=self.briefing,
            alarm=self.alarm,
            mac_status=self.mac_status
        )

        self.tts.speak(
            "Astra is online and ready."
        )



    def handle_command(self, command: str) -> str:

        if not command.strip():
            return "I didn't catch that."

        return self.router.handle(command)



    def run(self) -> None:

        while True:


            # SLEEP MODE
   
            wake_command = wait_for_wake_word()

            if wake_command is None:
                break



            # Morning briefing
            if wake_command == "good morning":

                briefing = self.briefing.get_briefing()

                self.tts.speak(briefing)

                print(
                    "Briefing complete."
                )

                continue



            # ACTIVE MODE

            self.tts.speak(
                "Hello master Daniel, how can I help?"
            )


            while True:

                print(
                    "Listening..."
                )


                command = self.speech.listen(
                    timeout=15,
                    phrase_time_limit=100
                )


                # No speech detected
                if not command:

                    if self.music_mode:

                        print(
                            "Spotify active. Continuing to listen..."
                        )

                        continue


                    print(
                        "No response detected."
                    )

                    self.tts.speak(
                        "Going back to sleep."
                    )

                    break



                lowered = command.lower()



                # Sleep Commands

                if any(
                    phrase in lowered
                    for phrase in [
                        "go to sleep",
                        "sleep mode",
                        "stop listening"
                    ]
                ):
                    self.music_mode = False

                    self.tts.speak(
                        "Going back to sleep."
                    )

                    break


                # Process Command

                print(
                    f"Command received: {command}"
                )

                if (
                    "im awake" in lowered
                    or "i'm awake" in lowered
                ):
                    print("Alarm dismissal command ignored.")
                    continue


                response = self.handle_command(
                    command
                )

                # Update music state

                if any(
                    phrase in lowered
                    for phrase in [
                        "pause",
                        "stop music",
                        "pause spotify"
                    ]
                ):

                    self.music_mode = False

                    if response:
                        self.tts.speak(response)

                    break


                elif any(
                    word in lowered
                    for word in [
                        "play",
                        "playlist",
                        "spotify"
                    ]
                ):

                    self.music_mode = True

                


                if response:

                    print(
                        f"Astra: {response}"
                    )

                    self.tts.speak(
                        response
                    )


                # Continue Conversation

                print(
                    "Listening for next command..."
                )