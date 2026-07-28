import subprocess
import shutil
import psutil


class MacStatusService:

    def __init__(self):
        pass


    def cpu_usage(self):

        cpu = psutil.cpu_percent(
            interval=1
        )

        return (
            f"CPU usage is currently "
            f"{cpu} percent."
        )


    def memory_usage(self):

        memory = psutil.virtual_memory()

        used = round(
            memory.used / (1024 ** 3),
            2
        )

        total = round(
            memory.total / (1024 ** 3),
            2
        )

        return (
            f"Memory usage is "
            f"{used} gigabytes out of "
            f"{total} gigabytes."
        )


    def disk_space(self):

        disk = shutil.disk_usage("/")

        free = round(
            disk.free / (1024 ** 3),
            2
        )

        total = round(
            disk.total / (1024 ** 3),
            2
        )

        return (
            f"You have {free} gigabytes "
            f"free out of {total} gigabytes."
        )


    def battery(self):

        battery = psutil.sensors_battery()

        if battery is None:
            return "Battery information unavailable."

        return (
            f"Battery is at "
            f"{battery.percent} percent."
        )


    def wifi_status(self):

        try:

            result = subprocess.check_output(
                [
                    "sh",
                    "-c",
                    "networksetup -getairportnetwork en0"
                ]
            ).decode()

            return result.strip()

        except:

            return "Wi-Fi status unavailable."


    def docker_status(self):

        try:

            result = subprocess.check_output(
                [
                    "docker",
                    "ps",
                    "--format",
                    "{{.Names}}"
                ]
            ).decode()

            containers = result.strip()

            if containers:
                return (
                    f"Docker is running with "
                    f"{len(containers.splitlines())} containers."
                )

            return "Docker is running but no containers are active."


        except:

            return "Docker is not running."


    def external_drives(self):

        try:

            result = subprocess.check_output(
                [
                    "df",
                    "-h"
                ]
            ).decode()


            drives = []

            for line in result.splitlines():

                if "/Volumes/" in line:

                    drives.append(
                        line.split()[-1]
                    )


            if drives:

                return (
                    "External drives connected: "
                    +
                    ", ".join(drives)
                )

            return "No external drives detected."


        except:

            return "External drive information unavailable."



    def full_status(self):

        status = (

            "Here is your Mac status. "

            +
            self.cpu_usage()
            +
            " "

            +
            self.memory_usage()
            +
            " "

            +
            self.disk_space()
            +
            " "

            +
            self.battery()
            +
            " "

            +
            self.wifi_status()
            +
            " "

            +
            self.docker_status()
            +
            " "

            +
            self.external_drives()

        )


        return status