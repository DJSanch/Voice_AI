import urllib.request
import json
import ssl
import certifi
import subprocess
import webbrowser


class NewsService:

    def __init__(self):
        self.api_key = "pub_904f349a5c5342e8b486b066955e21da"

        self.url = (
            "https://newsdata.io/api/1/news?"
            f"apikey={self.api_key}&"
            "country=us&"
            "language=en"
        )


    def get_news(self, topic=None):

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
                    "country=us&"
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

            if not articles:
                if topic:
                    return f"I couldn't find any news about {topic}."
                return "No news found."

            headlines = []

            if topic:
                headlines.append(
                    f"Here are the latest news about {topic}."
                )
            else:
                headlines.append(
                    "Here are today's top headlines."
                )

            for index, article in enumerate(articles[:5], start=1):

                title = article.get(
                    "title",
                    "Unknown headline"
                )

                headlines.append(
                    f"{index}. {title}"
                )

            return "\n\n".join(headlines)

        except Exception as e:
            print("News Error:", e)
            return "I couldn't get the news right now."
            
    def open_news(self):
        try:
            webbrowser.open(
                "https://news.google.com"
            )

        except Exception as e:
            print("Open news error:", e)
