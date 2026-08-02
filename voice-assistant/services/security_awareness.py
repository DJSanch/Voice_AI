import json
import os
from datetime import datetime


class SecurityAwarenessService:

    def __init__(self, network):

        self.network = network

        self.history_file = (
            "data/security_events.json"
        )

        self.ensure_storage()

        self.device_history = (
            self.load_history()
        )


    # --------------------------------
    # Storage
    # --------------------------------

    def ensure_storage(self):

        os.makedirs(
            "data",
            exist_ok=True
        )

        if not os.path.exists(
            self.history_file
        ):

            with open(
                self.history_file,
                "w"
            ) as file:

                json.dump(
                    [],
                    file,
                    indent=4
                )


    # --------------------------------
    # History
    # --------------------------------

    def load_history(self):

        try:

            with open(
                self.history_file,
                "r"
            ) as file:

                events = json.load(file)


            devices = {}


            for event in events:

                if (
                    event.get("event")
                    == "device_seen"
                ):

                    device = (
                        event["device"]
                    )

                    devices[
                        device["mac"]
                    ] = device


            return devices


        except Exception:

            return {}



    def save_event(
        self,
        event,
        device
    ):

        events = []


        try:

            with open(
                self.history_file,
                "r"
            ) as file:

                events = json.load(file)


        except:

            events = []


        events.append(

            {
                "time":
                    datetime.now()
                    .strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "event":
                    event,

                "device":
                    device
            }

        )


        with open(
            self.history_file,
            "w"
        ) as file:

            json.dump(
                events,
                file,
                indent=4
            )



    # --------------------------------
    # Risk Engine
    # --------------------------------

    def analyze_device(
        self,
        device
    ):

        score = 0
        reasons = []


        vendor = (
            device.get(
                "vendor",
                ""
            )
            .lower()
        )


        dtype = (
            device.get(
                "type",
                ""
            )
            .lower()
        )


        hostname = (
            device.get(
                "hostname",
                ""
            )
        )


        services = (
            device.get(
                "services",
                []
            )
        )


        # Unknown manufacturer

        if (
            "unknown"
            in vendor
        ):

            score += 20

            reasons.append(
                "Unknown manufacturer"
            )



        # Unknown device type

        if (
            "unknown"
            in dtype
        ):

            score += 20

            reasons.append(
                "Unknown device type"
            )



        # No hostname

        if hostname in [
            "",
            "?",
            "Unknown device"
        ]:

            score += 10

            reasons.append(
                "No device name detected"
            )



        # Many services

        if len(
            services
        ) >= 4:

            score += 20

            reasons.append(
                "Multiple network services"
            )



        # Classification

        if score >= 70:

            level = "High"


        elif score >= 30:

            level = "Medium"


        else:

            level = "Low"



        return {

            "score": score,

            "level": level,

            "reasons": reasons

        }



    # --------------------------------
    # New Device Detection
    # --------------------------------

    def detect_new_devices(self):

        devices = (
            self.network.scan_devices()
        )


        new_devices = []


        for device in devices:

            mac = device["mac"]


            if mac not in self.device_history:

                new_devices.append(
                    device
                )


                self.save_event(
                    "device_seen",
                    device
                )


                self.device_history[
                    mac
                ] = device


        return new_devices



    # --------------------------------
    # Security Report
    # --------------------------------

    def security_report(self):

        devices = (
            self.network.scan_devices()
        )


        report = (
            "Astra security report.\n\n"
        )


        counters = {

            "Low": 0,
            "Medium": 0,
            "High": 0

        }


        for device in devices:


            analysis = (
                self.analyze_device(
                    device
                )
            )


            level = (
                analysis["level"]
            )


            counters[level] += 1


            name = (
                device.get(
                    "hostname"
                )
            )


            if name in [
                "",
                "?",
                "Unknown device"
            ]:

                name = (
                    device.get(
                        "vendor",
                        "Unknown"
                    )
                )


            report += (

                f"{name}\n"

                f"IP: {device['ip']}\n"

                f"Manufacturer: "
                f"{device['vendor']}\n"

                f"Risk: {level} "
                f"({analysis['score']}%)\n"

            )


            if analysis["reasons"]:

                report += (
                    "Reasons: "
                    +
                    ", ".join(
                        analysis["reasons"]
                    )
                    +
                    "\n"
                )


            report += "\n"



        report += (

            f"Low risk devices: "
            f"{counters['Low']}\n"

            f"Medium risk devices: "
            f"{counters['Medium']}\n"

            f"High risk devices: "
            f"{counters['High']}"

        )


        return report