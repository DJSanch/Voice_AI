import urllib.request
import urllib.parse
import json
import ssl
import certifi
import webbrowser


class NewsService:

    def __init__(self):
        self.api_key = "pub_904f349a5c5342e8b486b066955e21da"

    def get_news(self, topic=None, country="us", limit=5):

        try:

            if topic:

                url = (
                    "https://newsdata.io/api/1/news?"
                    f"apikey={self.api_key}&"
                    f"q={urllib.parse.quote(topic)}&"
                    "language=en"
                )

            else:

                url = (
                    "https://newsdata.io/api/1/news?"
                    f"apikey={self.api_key}&"
                    f"country={country}&"
                    "language=en"
                )

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Astra Assistant"
                }
            )

            context = ssl.create_default_context(
                cafile=certifi.where()
            )

            with urllib.request.urlopen(
                request,
                context=context,
                timeout=10
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            articles = data.get("results", [])

            headlines = []

            for article in articles[:limit]:

                title = article.get(
                    "title",
                    "Unknown headline"
                )

                headlines.append(title)

            return headlines

        except Exception as e:

            print("News Error:", e)

            return []

    # ------------------------
    # Daily Briefing Categories
    # ------------------------

    def get_daily_news(self):

        return self.get_news()

    def get_badminton_news(self):

        return self.get_news(
            topic="Badminton OR BWF OR Viktor Axelsen OR An Se-young"
        )

    def get_ai_news(self):

        return self.get_news(
            topic="AI OR Artificial Intelligence OR OpenAI OR Anthropic OR Google DeepMind"
        )

    def get_technology_news(self):

        return self.get_news(
            topic="Technology OR Tech"
        )

    # ------------------------
    # Helper for Daily Briefing
    # ------------------------

    def get_daily_briefing_news(self):

        return {
            "Daily News": self.get_daily_news(),
            "Badminton": self.get_badminton_news(),
            "AI": self.get_ai_news(),
            "Technology": self.get_technology_news()
        }

    def open_news(self):

        try:

            webbrowser.open(
                "https://news.google.com"
            )

        except Exception as e:

            print("Open news error:", e)