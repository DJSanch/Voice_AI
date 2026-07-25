import json
import os
import plistlib
import re
import ssl
import sqlite3
import subprocess
import urllib.parse
import urllib.request

CONFIG_FILE = "config.json"





class NetworkTools:
    def _build_request(self, url: str) -> urllib.request.Request:
        return urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    def _get_default_city(self):
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)

            return config.get("city", "Scottsdale")

        except Exception:
            return "Scottsdale"

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

    def _get_device_coordinates(self) -> tuple[float, float] | None:
        if not CLLocationManager or not NSObject or not NSRunLoop or not NSDate:
            return None

        class LocationDelegate(NSObject):
            def init(self):
                self = objc.super(LocationDelegate, self).init()
                if self is None:
                    return None

                self.location = None
                self.error = None

                return self

            def locationManager_didUpdateLocations_(self, manager, locations):
                if locations:
                    loc = locations[-1]
                    coord = loc.coordinate()
                    self.location = (coord.latitude, coord.longitude)

            def locationManager_didFailWithError_(self, manager, error):
                print("Location Error:", error)
                self.failed = True
            
            def locationManagerDidChangeAuthorization_(self, manager):
                print("Authorization Changed:", manager.authorizationStatus())

                if manager.authorizationStatus() in (3, 4):
                    manager.startUpdatingLocation()

        delegate = LocationDelegate.alloc().init()
        manager = CLLocationManager.alloc().init()

        manager.setDelegate_(delegate)
        self._location_delegate = delegate
        self._location_manager = manager

        if hasattr(manager, "requestAlwaysAuthorization"):
            manager.requestAlwaysAuthorization()
        elif hasattr(manager, "requestWhenInUseAuthorization"):
            manager.requestWhenInUseAuthorization()

            print("Authorization after request:", manager.authorizationStatus())
            manager.setDesiredAccuracy_(kCLLocationAccuracyBest)

            manager.startUpdatingLocation()
            print("Started updating location...")
            timeout = NSDate.dateWithTimeIntervalSinceNow_(10)

            runloop = NSRunLoop.currentRunLoop()

        while delegate.location is None and delegate.error is None:
            if NSDate.date().compare_(timeout) == 1:
                break

            runloop.runUntilDate_(
                NSDate.dateWithTimeIntervalSinceNow_(0.1)
            )

        manager.stopUpdatingLocation()

        print("GPS:", delegate.location)

        return delegate.location

    def _extract_coords_from_url(self, url: str) -> tuple[float, float] | None:
        try:
            parts = urllib.parse.urlparse(url).path.split("/")
            for i, part in enumerate(parts):
                if part.startswith("en-") and i + 2 < len(parts):
                    lat = float(parts[i + 1])
                    lon = float(parts[i + 2])
                    return lat, lon
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
            request = self._build_request(url)
            request.add_header("User-Agent", "Mozilla/5.0")
            with urllib.request.urlopen(request, context=self._get_ssl_context(), timeout=10) as response:
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
            if location_name:
                location_part = f" in {location_name}"
            else:
                location_part = " in your current location"
            return f"The weather{location_part} is {condition_text} with a temperature of {temperature_text} degrees Celsius."
        except Exception:
            return None

    def fetch(self, url: str) -> str:
        request = self._build_request(url)
        with urllib.request.urlopen(request, context=self._get_ssl_context(), timeout=10) as response:
            return response.read().decode("utf-8")

    def get_weather(self, city: str | None = None) -> str:
        try:
            if city:
                url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
                location = city
            else:
                city = self._get_default_city()

                url = f"https://wttr.in/{urllib.parse.quote(city)}?format=j1"
                location = city

            request = self._build_request(url)

            with urllib.request.urlopen(
                request,
                context=self._get_ssl_context(),
                timeout=10
            ) as response:
                data = json.loads(response.read().decode("utf-8"))

            current = data["current_condition"][0]

            description = current["weatherDesc"][0]["value"]
            temperature = round(float(current["temp_C"]))

            return (
                f"The weather in {location} is "
                f"{description} with a temperature of "
                f"{temperature} degrees Celsius."
            )

        except Exception as e:
            print("Weather Error:", e)

            if city:
                return f"Unable to fetch weather for {city}."

            return "Unable to fetch weather for your current location."