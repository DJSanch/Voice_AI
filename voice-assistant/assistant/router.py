class CommandRouter:

    def __init__(
        self,
        weather,
        spotify,
        llm,
        system_tools,
        timer,
        notes,
        news,
        briefing
    ):
        self.weather = weather
        self.spotify = spotify
        self.llm = llm
        self.system_tools = system_tools
        self.timer = timer
        self.timer_waiting = False
        self.notes = notes
        self.news = news
        self.briefing = briefing
        


    def handle(self, command: str) -> str:
        text = command.strip()
        lowered = text.lower()

        if not text:
            return "I didn't catch that."
        
        # Daily Briefing

        if (
            "good morning" in lowered
            or "daily briefing" in lowered
            or "morning briefing" in lowered
        ):
            return self.briefing.get_briefing()

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
            self.weather.open_weather()
            return self.weather.get_weather(city)


        # Spotify Controls

        # Current song
        if (
            "what song" in lowered
            or "what's playing" in lowered
            or "currently playing" in lowered
        ):
            return self.spotify.current_song()

        # Pause / Stop
        if (
            "pause" in lowered
            or "stop" in lowered
        ):
            return self.spotify.pause()

        # Resume
        if (
            "resume music" in lowered
            or "resume spotify" in lowered
            or lowered == "resume"
            or lowered == "continue music"
        ):
            return self.spotify.resume()

        # Next song
        if (
            "next" in lowered
            or "skip" in lowered
        ):
            return self.spotify.next_song()

        # Previous song
        if (
            "previous" in lowered
            or "back" in lowered
        ):
            return self.spotify.previous_song()

        # Play music
        if any(
            word in lowered
            for word in [
                "play",
                "spotify",
                "music"
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
        
        # Notes
        if "take a note" in lowered or "remember" in lowered:

            note = text

            if "take a note" in lowered:
                note = text.lower().split(
                    "take a note",
                    1
                )[1].strip()

            elif "remember" in lowered:
                note = text.lower().split(
                    "remember",
                    1
                )[1].strip()


            return self.notes.add_note(note)



        if "show my notes" in lowered or "read my notes" in lowered:

            return self.notes.get_notes()



        if "clear my notes" in lowered:

            return self.notes.clear_notes()
        
        # News
        if (
            "news" in lowered
            or "headline" in lowered
            or "headlines" in lowered
        ):

            topic = None

            # Topic search
            if "news for " in lowered:
                topic = text.split("news for", 1)[1].strip()

            elif "news regarding " in lowered:
                topic = text.split("news regarding", 1)[1].strip()

            self.news.open_news()

            return self.news.get_news(topic)

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