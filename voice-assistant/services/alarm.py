import datetime
import threading
import time


class AlarmService:

    def __init__(
        self,
        briefing,
        spotify,
        tts,
        speech
    ):

        self.briefing = briefing
        self.spotify = spotify
        self.tts = tts
        self.speech = speech
        self.alarm_time = None
        self.running = True
        self.alarm_active = False

        thread = threading.Thread(
            target=self.monitor,
            daemon=True
        )

        thread.start()


    def set_alarm(self, alarm_time):

        try:
            parsed = datetime.datetime.strptime(
                alarm_time,
                "%H:%M"
            )

            self.alarm_time = parsed.strftime("%H:%M")

        except Exception:

            return "I couldn't understand the alarm time."

        return f"Alarm set for {self.alarm_time}."

    def monitor(self):

        while self.running:

            if self.alarm_time:

                now = datetime.datetime.now()

                current = now.strftime(
                    "%H:%M"
                )

                if current == self.alarm_time:

                    self.trigger()

                    self.alarm_time = None


            time.sleep(20)



    def trigger(self):

        self.alarm_active = True

        alarm_thread = threading.Thread(
            target=self.play_alarm_sound,
            daemon=True
        )

        alarm_thread.start()


        while self.alarm_active:

            command = self.speech.listen(
                timeout=30,
                phrase_time_limit=5
            )


            if not command:
                continue


            lowered = command.lower().strip()

            print(
                f"Alarm heard: {lowered}"
            )

            if any(
                phrase in lowered
                for phrase in [
                    "i'm awake",
                    "im awake"
                ]
            ):

                self.stop_alarm()

                return


    def play_alarm_sound(self):

        while self.alarm_active:

            import subprocess

            subprocess.run(
                [
                    "afplay",
                    "/System/Library/Sounds/Submarine.aiff"
                ]
            )

            time.sleep(1)


        
    def stop_alarm(self):

        print("Alarm dismissed.")

        self.alarm_active = False

        time.sleep(0.5)

        briefing = self.briefing.get_briefing()

        self.tts.speak(
            briefing
        )

        self.spotify.play(
            "morning playlist"
        )