import re

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
        briefing,
        alarm,
        mac_status,
        vision,
        hand_tracking,
        network,
        security,
        plugin_manager

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
        self.alarm = alarm
        self.mac_status = mac_status
        self.vision = vision
        self.hand_tracking = hand_tracking
        self.network = network
        self.pending_action = None
        self.pending_devices = []
        self.selected_device = None
        self.security = security
        self.plugin_manager = plugin_manager


    def handle(self, command: str) -> str:

        plugin = self.plugin_manager.find_plugin(command)

        if plugin:
            return plugin.handle(command)

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



        
        # Open applications
        if lowered.startswith("open ") or lowered.startswith("launch "):

            app = text

            if lowered.startswith("open "):
                app = text[5:].strip()

            elif lowered.startswith("launch "):
                app = text[7:].strip()

            return self.system_tools.open_application(app)

        
        
        # News
        if (
            "news" in lowered
            or "headline" in lowered
            or "headlines" in lowered
        ):

            topic = None


            # Category detection

            if "badminton" in lowered:

                headlines = self.news.get_badminton_news()
                category = "Badminton"


            elif (
                "ai" in lowered
                or "artificial intelligence" in lowered
            ):

                headlines = self.news.get_ai_news()
                category = "AI"


            elif (
                "technology" in lowered
                or "tech" in lowered
            ):

                headlines = self.news.get_technology_news()
                category = "Technology"


            # Custom search

            elif "news for " in lowered:

                topic = text.split(
                    "news for",
                    1
                )[1].strip()

                headlines = self.news.get_news(topic)
                category = topic


            elif "news regarding " in lowered:

                topic = text.split(
                    "news regarding",
                    1
                )[1].strip()

                headlines = self.news.get_news(topic)
                category = topic


            else:

                headlines = self.news.get_daily_news()
                category = "Daily News"



            print(
                f"\n========== {category.upper()} =========="
            )


            if headlines:

                news_text = (
                    f"Here are the latest {category} updates. "
                )


                for index, headline in enumerate(
                    headlines,
                    start=1
                ):

                    print(
                        f"{index}. {headline}"
                    )

                    news_text += (
                        headline + ". "
                    )


            else:

                print(
                    "No news available."
                )

                news_text = (
                    f"I couldn't find any {category} news right now."
                )


            print(
                "================================\n"
            )


            return news_text
        
            
        
        # Object Identification

        if (
            "what am i holding" in lowered
            or "identify this object" in lowered
            or "what is this" in lowered
        ):

            image = self.hand_tracking.capture_hand_region()


            if image:

                return self.vision.analyze_object(
                    image
                )


            return "I couldn't capture the object."
        
        
        # -----------------------------
        # Device Learning Memory
        # -----------------------------


        if self.pending_action == "remember_device":

            for device in self.pending_devices:

                if (
                    lowered in device["vendor"].lower()
                    or lowered in device["type"].lower()
                ):

                    self.selected_device = device

                    self.pending_action = "device_name"


                    return (
                        f"I found {device['vendor']}. "
                        "What name should I save for this device?"
                    )



        if self.pending_action == "device_name":

            name = text.strip()


            self.network.memory.add_device(

                mac=self.selected_device["mac"],

                name=name,

                device_type=self.selected_device["type"]

            )


            self.pending_action = None

            self.pending_devices = []

            return (
                f"Saved. I will remember "
                f"{name}."
            )



        if "remember this device" in lowered:

            devices = self.network.scan_devices()


            self.pending_action = "remember_device"

            self.pending_devices = devices


            return (
                f"I found {len(devices)} devices. "
                "Which device should I remember?"
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