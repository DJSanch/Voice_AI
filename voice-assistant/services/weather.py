import json
import os
import subprocess
import urllib.parse
import urllib.request

from tools.network import NetworkTools


CONFIG_FILE = "config.json"


class WeatherService:

    def __init__(self):
        self.network = NetworkTools()


    def _get_default_city(self):
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)

            return config.get("city", "Scottsdale")

        except Exception:
            return "Scottsdale"


    def open_weather(self):
        """
        Opens macOS Weather application
        """
        try:
            subprocess.run(
                ["open", "-a", "Weather"],
                check=False
            )

        except Exception as e:
            print("Weather App Error:", e)



    def get_weather(self, city: str | None = None):

        try:

            if city:
                location = city
            else:
                location = self._get_default_city()


            url = (
                f"https://wttr.in/"
                f"{urllib.parse.quote(location)}?format=j1"
            )


            request = self.network.build_request(url)


            with urllib.request.urlopen(
                request,
                context=self.network.ssl_context(),
                timeout=10
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )


            current = data["current_condition"][0]


            description = current["weatherDesc"][0]["value"]

            temperature = round(
                float(current["temp_C"])
            )

            feels_like = current["FeelsLikeC"]

            humidity = current["humidity"]

            uv = current["uvIndex"]


            recommendation = self._weather_recommendation(
                temperature,
                feels_like,
                humidity,
                uv,
                description
            )


            return (
                f"Currently in {location}, "
                f"it is {description}. "
                f"The temperature is {temperature} degrees Celsius. "
                f"It feels like {feels_like} degrees. "
                f"Humidity is {humidity} percent. "
                f"UV index is {uv}. "
                f"{recommendation}"
            )


        except Exception as e:

            print("Weather Error:", e)

            if city:
                return f"Unable to fetch weather for {city}."

            return "Unable to fetch your weather."



    def _weather_recommendation(
        self,
        temperature,
        feels_like,
        humidity,
        uv,
        condition
    ):

        recommendations = []


        feels = int(feels_like)
        uv = int(uv)

        condition = condition.lower()


        if feels >= 40:

            recommendations.append(
                "It is extremely hot outside. Stay hydrated and avoid long outdoor activities."
            )


        elif feels >= 32:

            recommendations.append(
                "It is warm outside. Bring water if you plan to stay outdoors."
            )


        if uv >= 8:

            recommendations.append(
                "UV levels are high. Consider sunscreen or staying in shaded areas."
            )


        if "rain" in condition:

            recommendations.append(
                "Rain is expected. Consider bringing an umbrella."
            )


        if not recommendations:

            recommendations.append(
                "Weather conditions look comfortable for outdoor activities."
            )


        return " ".join(recommendations)