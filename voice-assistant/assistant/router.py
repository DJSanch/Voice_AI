class CommandRouter:

    def __init__(
        self,
        weather,
        spotify,
        llm,
        system_tools,
        timer
    ):
        self.weather = weather
        self.spotify = spotify
        self.llm = llm
        self.system_tools = system_tools
        self.timer = timer
        self.timer_waiting = False


    def handle(self, command: str) -> str:
        text = command.strip()
        lowered = text.lower()

        if not text:
            return "I didn't catch that."


        # Greetings
        if lowered in {
            "hello",
            "hi",
            "hey",
            "hey there"
        }:
            return "Hello! How can I help you?"


        # Weather
        if "weather" in lowered:
            city = None

            if " in " in lowered:
                city = text.lower().split(" in ", 1)[1].title()

            return self.weather.get_weather(city)


        # Spotify
        if any(
            word in lowered
            for word in [
                "play",
                "music",
                "song",
                "spotify"
            ]
        ):
            query = text

            if lowered.startswith("play"):
                query = text[4:].strip()

            return self.spotify.play(query)
        
        # Open applications
        if lowered.startswith("open ") or lowered.startswith("launch "):

            app = text

            if lowered.startswith("open "):
                app = text[5:].strip()

            elif lowered.startswith("launch "):
                app = text[7:].strip()

            return self.system_tools.open_application(app)
        
        # Timer
        if "timer" in lowered or self.timer_waiting:

            self.timer_waiting = False

            words = lowered.split()

            for word in words:
                if word.isdigit():

                    minutes = int(word)

                    return self.timer.set_timer(
                        minutes,
                        callback=self.system_tools.speak
                    )


            if "one" in lowered:
                return self.timer.set_timer(
                    1,
                    callback=self.system_tools.speak
                )


            self.timer_waiting = True
            return "How many minutes should I set the timer for?"
        
          # Time
        if lowered in [
            "time",
            "what time is it",
            "what is the time",
            "tell me the time"
        ]:
            return (
                f"The current time is "
                f"{self.system_tools.get_current_time()}."
            )


        # Everything else → LLM
        prompt = (
            "You are a helpful voice assistant. "
            "Keep your answer short and conversational.\n"
            f"User: {text}\n"
            "Assistant:"
        )

        response = self.llm.ask(prompt)

        if response:
            return response

        return "I couldn't find an answer."