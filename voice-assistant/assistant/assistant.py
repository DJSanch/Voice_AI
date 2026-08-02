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
from services.vision import VisionService
from services.selection import SelectionService
from services.hand_tracking import HandTrackingService
from services.network_awareness import NetworkAwarenessService
from services.security_awareness import SecurityAwarenessService
from services.dashboard import update_dashboard_state
from plugins.plugin_manager import PluginManager


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
        self.selection = SelectionService()
        self.vision = VisionService(
            llm=self.llm,
            selection=self.selection
        )
        self.hand_tracking = HandTrackingService()
        self.network = NetworkAwarenessService(
            self.tts
        )
        self.security = SecurityAwarenessService(
            self.network
        )

        self.pending_action = None
        self.pending_devices = []


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


                # Plugin
        self.plugin_manager = PluginManager()

        services = {
            "weather": self.weather,
            "mac_status": self.mac_status,
            "network": self.network,
            "security": self.security,
            "spotify": self.spotify,
            "notes": self.notes,
            "timer": self.timer,
            "system_tools": self.system_tools,
            "alarm": self.alarm,
            "vision": self.vision,
            "hand_tracking": self.hand_tracking,
            "plugin_manager": self.plugin_manager,
            "tts": self.tts,
        }

        self.plugin_manager.load_plugins(services)


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
            mac_status=self.mac_status,
            vision=self.vision,
            hand_tracking=self.hand_tracking,
            network=self.network,
            security=self.security,
            plugin_manager=self.plugin_manager
        )

        update_dashboard_state(
            status="online",
            mode="sleep",
            activity="Astra is online and ready.",
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
   
            update_dashboard_state(
                status="listening",
                mode="wake",
                activity="Listening for wake word",
            )

            wake_command = wait_for_wake_word()

            if wake_command is None:
                update_dashboard_state(
                    status="idle",
                    mode="sleep",
                    activity="Wake word not detected",
                )
                break



            # Morning briefing
            if wake_command == "good morning":

                briefing = self.briefing.get_briefing()

                update_dashboard_state(
                    status="speaking",
                    mode="briefing",
                    activity="Delivered morning briefing",
                    last_response=briefing,
                )

                self.tts.speak(briefing)

                print(
                    "Briefing complete."
                )

                continue



            # ACTIVE MODE

            update_dashboard_state(
                status="active",
                mode="conversation",
                activity="Awaiting your voice command",
            )

            self.tts.speak(
                "Hello master Daniel, how can I help?"
            )


            while True:

                print(
                    "Listening..."
                )

                update_dashboard_state(
                    status="listening",
                    mode="conversation",
                    activity="Listening for a command",
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
                update_dashboard_state(
                    status="processing",
                    mode="conversation",
                    activity="Received a voice command",
                    last_command=command,
                )

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

                update_dashboard_state(
                    status="responding",
                    mode="conversation",
                    activity="Processed the voice command",
                    last_command=command,
                    last_response=response,
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