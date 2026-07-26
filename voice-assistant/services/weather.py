import json
import os
import plistlib
import re
import sqlite3
import subprocess
import urllib.parse
import urllib.request

from tools.network import NetworkTools

CONFIG_FILE = "config.json"

class WeatherService:

    def _get_default_city(self):
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)

            return config.get("city", "Scottsdale")

        except Exception:
            return "Scottsdale"

    def _get_apple_weather_token(self) -> str | None:
        try:
            prefs_path = os.path.expanduser(
                "~/Library/Containers/com.apple.weather/Data/Library/Preferences/com.apple.weather.plist"
            )
            if not os.path.exists(prefs_path):
                return None
            with open(prefs_path, "rb") as handle:
                prefs = plistlib.load(handle)
            return prefs.get("wdsAuthToken")
        except Exception:
            return None
        
    def _format_condition(self, condition: str | None) -> str:
        if not condition:
            return "clear"
        words = re.sub(r"([a-z])([A-Z])", r"\1 \2", str(condition))
        return words.lower()
    
    def _format_temperature(self, temperature) -> str:
        try:
            return str(int(round(float(temperature))))
        except (TypeError, ValueError):
            return str(temperature)
    

    def _get_weatherkit_cache_url(self) -> str | None:
        cache_db = os.path.expanduser(
            '~/Library/Containers/com.apple.weather/Data/Library/Caches/com.apple.weather/Cache.db'
        )
        if not os.path.exists(cache_db):
            return None
        try:
            conn = sqlite3.connect(cache_db)
            cur = conn.cursor()
            cur.execute(
                "SELECT request_key FROM cfurl_cache_response WHERE request_key LIKE '%weatherkit.apple.com/api/v2/weather%' ORDER BY time_stamp DESC LIMIT 1"
            )
            row = cur.fetchone()
            conn.close()
            if row:
                return row[0]
        except Exception:
            pass
        return None
    
    def _reverse_geocode_location(self, latitude: float, longitude: float) -> str | None:
        try:
            query = urllib.parse.urlencode({
                "format": "jsonv2",
                "lat": str(latitude),
                "lon": str(longitude),
                "zoom": "10",
                "addressdetails": "1",
            })
            url = f"https://nominatim.openstreetmap.org/reverse?{query}"
            request = self.network.build_request(url)
            request.add_header("User-Agent", "Mozilla/5.0")
            with urllib.request.urlopen(request, context=self.network.ssl_context(), timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            address = data.get("address", {})
            for key in ["city", "town", "village", "state", "county", "country"]:
                if key in address:
                    return address[key]
        except Exception:
            pass
        return None
    
    def _get_weather_app_location(self) -> str | None:
        try:
            script = 'tell application "Weather" to activate\n delay 0.5\n tell application "System Events" to tell process "Weather" to return name of window 1'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, check=False)
            name = result.stdout.strip()
            if name:
                return name
        except Exception:
            pass
        return None

    def _get_apple_weather(self) -> str | None:
        token = self._get_apple_weather_token()
        if not token:
            return None

        location_name = self._get_weather_app_location()
        url = self._get_weatherkit_cache_url()
        if not url:
            return None

        coords = self._extract_coords_from_url(url)
        if not location_name and coords:
            location_name = self._reverse_geocode_location(*coords)

        try:
            request = self.network.build_request(url)
            request.add_header("Authorization", f"Bearer {token}")
            with urllib.request.urlopen(request, context=self.network.ssl_context(), timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
            current = data.get("currentWeather", {})
            temperature = current.get("temperature")
            condition = current.get("conditionCode")
            if temperature is None:
                return None
            condition_text = self._format_condition(condition)
            temperature_text = self._format_temperature(temperature)
            if location_name:
                location_part = f" in {location_name}"
            else:
                location_part = " in your current location"
            return f"The weather{location_part} is {condition_text} with a temperature of {temperature_text} degrees Celsius."
        except Exception:
            return None

    def get_weather(self, city: str | None = None) -> str:
        try:
            if city:
                url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
                location = city
            else:
                city = self._get_default_city()

                url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
                location = city

            request = self.network.build_request(url)

            with urllib.request.urlopen(
                request,
                context=self.network.ssl_context(),
                timeout=10
            ) as response:
                data = json.loads(response.read().decode("utf-8"))

            current = data["current_condition"][0]

            description = current["weatherDesc"][0]["value"]
            temperature = round(float(current["temp_C"]))
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

            feels_like = current["FeelsLikeC"]
            humidity = current["humidity"]
            wind = current["windspeedKmph"]
            wind_direction = current["winddir16Point"]
            uv = current["uvIndex"]

            return (
                f"Currently in {location}, it is {description}. "
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

            return "Unable to fetch weather for your current location."    
        
    def _weather_recommendation(
        self,
        temperature,
        feels_like,
        humidity,
        uv,
        condition
    ):

        recommendations = []

        temp = int(temperature)
        feels = int(feels_like)
        uv = int(uv)
        humidity = int(humidity)

        condition = condition.lower()


        # Heat
        if feels >= 40:
            recommendations.append(
                "It is extremely hot outside. Stay hydrated and avoid long outdoor activities."
            )

        elif feels >= 32:
            recommendations.append(
                "It is warm outside. Bring water if you plan to stay outdoors."
            )


        # UV
        if uv >= 8:
            recommendations.append(
                "UV levels are high. Consider sunscreen or staying in shaded areas."
            )


        # Rain
        if "rain" in condition:
            recommendations.append(
                "Rain is expected. Consider bringing an umbrella."
            )


        # Wind
        # You can add wind speed later


        # Good weather
        if not recommendations:
            recommendations.append(
                "Weather conditions look comfortable for outdoor activities."
            )


        return " ".join(recommendations)

    def __init__(self):
        self.network = NetworkTools()