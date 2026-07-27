from datetime import datetime
from time import sleep


class BriefingService:

    def __init__(
        self,
        weather,
        news,
        notes,
        system_tools,
        tts
    ):
        self.weather = weather
        self.news = news
        self.notes = notes
        self.system_tools = system_tools
        self.tts = tts


    def get_briefing(self):

        current_time = self.system_tools.get_current_time()

        self.tts.speak(
            "Good morning Master Daniel"
        )

        self.tts.speak(
            f"The current time is {current_time}"
        )

        self.weather.open_weather()

        weather = self.weather.get_weather()

        self.tts.speak(weather)

        sleep(0.1)

        self.news.open_news()

        news = self.news.get_news()

        self.tts.speak(news)

        sleep(0.1)

        notes = self.notes.get_notes()

        self.tts.speak(notes)

        self.tts.speak(
        "That's everything for your morning briefing. Have a wonderful day Master Daniel."
        )

        return "Morning briefing complete."