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


    def get_briefing(self, on_progress=None):

        print("\n========== ASTRA MORNING BRIEFING ==========\n")
        briefing_lines = ["========== ASTRA MORNING BRIEFING ==========", "", "TIME", "--------------------"]

        def publish_progress():
            if on_progress:
                on_progress("\n".join(briefing_lines))


        # Time
        current_time = self.system_tools.get_current_time()

        print("TIME")
        print("--------------------")
        print(current_time)
        print()
        briefing_lines.extend([current_time, "", "WEATHER", "--------------------"])


        # Weather
        print("WEATHER")
        print("--------------------")

        self.weather.open_weather()

        weather = self.weather.get_weather()

        print(weather)
        print()
        briefing_lines.extend([weather, "", "NEWS", "--------------------"])



        # News
        print("NEWS")
        print("--------------------")

        news_categories = self.news.get_daily_briefing_news()

        news_text = "Here are today's news updates. "

        for category, headlines in news_categories.items():

            print(f"\n{category}")
            print("--------------------")
            briefing_lines.extend(["", category, "--------------------"])

            news_text += f"{category}. "

            if headlines:

                for index, headline in enumerate(headlines, start=1):

                    print(f"{index}. {headline}")
                    briefing_lines.append(f"{index}. {headline}")

                    news_text += headline + ". "

            else:

                print("No news available.")
                briefing_lines.append("No news available.")

                news_text += "No news available. "



        print("\n")


        # Notes
        print("NOTES")
        print("--------------------")

        notes = self.notes.get_notes()

        print(notes)
        print()
        briefing_lines.extend(["", "NOTES", "--------------------", notes, "", "============================================", "Morning briefing complete."])
        publish_progress()

        print("============================================")
        print("Morning briefing complete.\n")

        self.tts.speak(
            f"Good morning Master Daniel. "
            f"The current time is {current_time}."
        )
        self.tts.speak(weather)
        self.tts.speak(news_text)
        self.tts.speak(notes)
        self.tts.speak(
            "That's everything for your morning briefing. "
            "Have a wonderful day Master Daniel."
        )


        return "\n".join(briefing_lines)
