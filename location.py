import json
import os

CONFIG_FILE = "config.json"


def get_city():
    if not os.path.exists(CONFIG_FILE):
        return "Scottsdale"

    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)

    return config.get("city", "Scottsdale")


def set_city(city):
    config = {
        "city": city
    }

    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)

    return f"Location changed to {city}"