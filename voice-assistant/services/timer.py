import threading
import time


class TimerService:

    def __init__(self):
        self.active_timer = None
        self.waiting_for_duration = False


    def set_timer(self, minutes, callback=None):

        if self.active_timer:
            return "A timer is already running."

        seconds = minutes * 60

        self.active_timer = threading.Thread(
            target=self._run_timer,
            args=(seconds, callback),
            daemon=True
        )

        self.active_timer.start()

        return f"Timer set for {minutes} minutes."


    def _run_timer(self, seconds, callback):

        time.sleep(seconds)

        self.active_timer = None

        if callback:
            callback("Your timer is finished.")