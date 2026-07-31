import json
import os


class DeviceMemory:


    def __init__(self):

        self.file = "known_devices.json"


    def load(self):

        if not os.path.exists(self.file):
            return {}

        with open(self.file) as f:
            return json.load(f)



    def save(self, devices):

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
        device_type
    ):

        devices = self.load()


        devices[mac] = {

            "name": name,

            "type": device_type

        }


        self.save(
            devices
        )



    def get_device(
        self,
        mac
    ):

        devices = self.load()

        return devices.get(
            mac
        )