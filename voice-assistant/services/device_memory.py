import json
import os
from datetime import datetime


class DeviceMemory:

    def __init__(self):

        self.file = "data/known_devices.json"


    def load(self):

        if not os.path.exists(self.file):
            return {}


        try:

            with open(self.file, "r") as f:
                return json.load(f)


        except json.JSONDecodeError:

            return {}



    def save(self, devices):

        os.makedirs(
            "data",
            exist_ok=True
        )


        with open(
            self.file,
            "w"
        ) as f:

            json.dump(
                devices,
                f,
                indent=4
            )



    def add_device(
        self,
        mac,
        name,
        device_type,
        owner="Daniel"
    ):

        devices = self.load()


        devices[mac] = {

            "name": name,

            "type": device_type,

            "owner": owner,

            "times_seen": 0,

            "first_seen": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            ),

            "last_seen": datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )

        }


        self.save(devices)



    def get_device(
        self,
        mac
    ):

        devices = self.load()


        device = devices.get(mac)


        if not device:
            return None


        device["times_seen"] = (
            device.get(
                "times_seen",
                0
            ) + 1
        )


        device["last_seen"] = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
        )


        self.save(devices)


        return device