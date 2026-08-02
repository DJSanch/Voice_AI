from plugins.base_plugin import BasePlugin


class TimerPlugin(BasePlugin):

    name = "Timer Plugin"
    version = "1.0"


    def __init__(self, timer, system_tools):

        self.timer = timer
        self.system_tools = system_tools
        self.waiting = False



    def can_handle(self, command):

        text = command.lower()

        return (
            "timer" in text
            or self.waiting
        )



    def handle(self, command):

        text = command.lower()


        words = text.split()


        for word in words:

            if word.isdigit():

                self.waiting = False

                return self.timer.set_timer(
                    int(word),
                    callback=self.system_tools.speak
                )



        if "one" in text:

            self.waiting = False

            return self.timer.set_timer(
                1,
                callback=self.system_tools.speak
            )



        self.waiting = True

        return (
            "How many minutes should I set the timer for?"
        )