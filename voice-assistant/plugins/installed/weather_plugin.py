from plugins.base_plugin import BasePlugin


class WeatherPlugin(BasePlugin):

    name = "Weather Plugin"
    version = "1.0"
    description = "Provides weather information"


    def __init__(self, weather_service):

        self.weather = weather_service


    def can_handle(self, command):

        return "weather" in command.lower()


    def handle(self, command):

        text = command.lower()

        city = None


        if " in " in text:

            city = (
                text
                .split(" in ",1)[1]
                .title()
            )


        self.weather.open_weather()

        return self.weather.get_weather(city)