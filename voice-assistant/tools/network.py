import json
import os
import plistlib
import re
import ssl
import urllib.request


class NetworkTools:
    def _build_request(self, url: str) -> urllib.request.Request:
        return urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    def _get_ssl_context(self):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return context

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

    def _get_apple_weather(self) -> str | None:
        token = self._get_apple_weather_token()
        if not token:
            return None

        try:
            url = "https://weatherkit.apple.com/api/v1/weather/en_US/0/0?dataSets=currentWeather"
            request = self._build_request(url)
            request.add_header("Authorization", f"Bearer {token}")
            with urllib.request.urlopen(request, context=self._get_ssl_context(), timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
            current = data.get("currentWeather", {})
            temperature = current.get("temperature")
            condition = current.get("conditionCode")
            if temperature is None:
                return None
            condition_text = self._format_condition(condition)
            temperature_text = self._format_temperature(temperature)
            return f"The current weather is {condition_text} with a temperature of {temperature_text} degrees Celsius."
        except Exception:
            return None

    def fetch(self, url: str) -> str:
        request = self._build_request(url)
        with urllib.request.urlopen(request, context=self._get_ssl_context(), timeout=10) as response:
            return response.read().decode("utf-8")

    def get_weather(self, city: str | None = None) -> str:
        try:
            apple_weather = self._get_apple_weather()
            if apple_weather:
                return apple_weather

            if city:
                url = f"https://wttr.in/{city.replace(' ', '+')}?format=j1"
            else:
                url = "https://wttr.in/?format=j1"
            request = self._build_request(url)
            with urllib.request.urlopen(request, context=self._get_ssl_context(), timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            current = data.get("current_condition", [{}])[0]
            nearest_area = data.get("nearest_area", [{}])[0]
            area_name = nearest_area.get("areaName", [{}])[0].get("value", "your location")
            area_country = nearest_area.get("country", [{}])[0].get("value", "")
            location = f"{area_name}, {area_country}".strip(", ")
            description = current.get("weatherDesc", [{}])[0].get("value", "unknown")
            temperature = current.get("temp_C", "unknown")
            try:
                temperature_text = str(int(round(float(temperature))))
            except (TypeError, ValueError):
                temperature_text = str(temperature)
            return f"The weather in {location} is {description} with a temperature of {temperature_text} degrees Celsius."
        except Exception:
            if city:
                return f"Unable to fetch weather for {city}."
            return "Unable to fetch weather for your current location."
