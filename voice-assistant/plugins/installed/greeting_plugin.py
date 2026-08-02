from plugins.base_plugin import BasePlugin


class GreetingPlugin(BasePlugin):

    name = "Greeting Plugin"
    version = "1.0"
    description = "Handles greetings and thanks"


    def can_handle(self, command):

        text = command.lower()

        return text in [
            "hello",
            "hi",
            "hey",
            "hey there"
        ] or any(
            phrase in text
            for phrase in [
                "thank you",
                "thanks",
                "i appreciate it"
            ]
        )


    def handle(self, command):

        text = command.lower()


        if any(
            phrase in text
            for phrase in [
                "thank you",
                "thanks",
                "i appreciate it"
            ]
        ):

            return "You're welcome, master Daniel."


        return "Hello! How can I help you?"