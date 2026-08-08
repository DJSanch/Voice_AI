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
from services.dashboard import get_dashboard_command, update_dashboard_state
from plugins.plugin_manager import PluginManager
from threading import Lock, Thread


class VoiceAssistant:

    def __init__(self, name: str = "Astra") -> None:

        self.name = name
        # Speech
        self.speech = SpeechController()
        self.tts = TextToSpeech()
        self.music_mode = False
        self._command_lock = Lock()
        self._briefing_lock = Lock()

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
            status="ready",
            activity="Astra is online and ready.",
            live_response="",
        )
        Thread(
            target=self._run_dashboard_commands,
            daemon=True,
            name="astra-dashboard-commands",
        ).start()

        self.tts.speak(
            "Astra is online and ready."
        )



    def handle_command(self, command: str) -> str:

        if not command.strip():
            return "I didn't catch that."

        with self._command_lock:
            return self.router.handle(command)


    def _run_dashboard_commands(self) -> None:
        """Run dashboard commands without waiting for microphone input."""
        while True:
            command = get_dashboard_command(timeout=1)
            if not command:
                continue

            lowered = command.lower()
            update_dashboard_state(
                status="processing",
                activity="Processing a Dashboard command.",
                last_command=command,
                live_response=f"Working on: {command}",
            )

            is_briefing = any(
                phrase in lowered
                for phrase in ("good morning", "daily briefing", "morning briefing")
            )
            if is_briefing:
                response = self._deliver_briefing()
                if response is None:
                    continue
            else:
                response = self.handle_command(command)
                update_dashboard_state(
                    status="responding",
                    activity="Astra is responding to your Dashboard request.",
                    last_command=command,
                    last_response=response,
                )
                if response:
                    self.tts.speak(response)

            update_dashboard_state(
                status="ready",
                activity="Astra has completed your Dashboard request.",
                last_command=command,
                last_response=response if is_briefing else None,
            )


    def _publish_briefing_progress(self, briefing: str) -> None:
        update_dashboard_state(
            status="responding",
            activity="Delivering your morning briefing.",
            live_response=briefing,
        )


    def _deliver_briefing(self) -> str | None:
        """Deliver one briefing at a time to prevent wake-word echo repeats."""
        if not self._briefing_lock.acquire(blocking=False):
            return None
        try:
            return self.briefing.get_briefing(
                on_progress=self._publish_briefing_progress
            )
        finally:
            self._briefing_lock.release()



    def run(self) -> None:

        while True:


            # SLEEP MODE
   
            update_dashboard_state(
                status="listening",
                activity="Listening for the wake word.",
            )
            wake_command = wait_for_wake_word()

            if wake_command is None:
                update_dashboard_state(
                    status="offline",
                    activity="Voice session ended.",
                )
                break

            # Morning briefing
            if wake_command == "good morning":

                briefing = self._deliver_briefing()
                if briefing is None:
                    continue

                update_dashboard_state(
                    status="responding",
                    activity="Delivering your morning briefing.",
                    last_response=briefing,
                )

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

                update_dashboard_state(
                    status="listening",
                    activity="Listening for a voice command.",
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

                if self.music_mode:
                    is_pause_command = any(
                        phrase in lowered
                        for phrase in ("pause", "stop music", "pause spotify")
                    )
                    is_next_command = any(
                        phrase in lowered
                        for phrase in ("next", "skip")
                    )
                    if not (is_pause_command or is_next_command):
                        update_dashboard_state(
                            status="listening",
                            activity="Music is playing. Listening for pause or next.",
                        )
                        print("Music mode: ignored non-playback command.")
                        continue

                update_dashboard_state(
                    status="processing",
                    activity="Processing your voice command.",
                    last_command=command,
                    live_response=f"Working on: {command}",
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
                    activity="Astra has completed your request.",
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

                


                is_briefing = any(
                    phrase in lowered
                    for phrase in ["good morning", "daily briefing", "morning briefing"]
                )

                if response and not is_briefing:

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
