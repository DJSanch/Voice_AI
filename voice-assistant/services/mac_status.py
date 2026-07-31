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

        percent = memory.percent

        return (
            f"Memory usage is {used} gigabytes "
            f"out of {total} gigabytes, "
            f"which is {percent} percent."
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
        
    
    def recommendations(self):

        recommendations = []

        # CPU
        cpu = psutil.cpu_percent(interval=0.5)

        if cpu >= 90:
            recommendations.append(
                "CPU usage is very high. Consider closing demanding applications or checking Activity Monitor."
            )

        elif cpu >= 70:
            recommendations.append(
                "CPU usage is moderately high. If your Mac feels slow, close unused applications."
            )


        # Memory
        memory = psutil.virtual_memory()

        if memory.percent >= 90:
            recommendations.append(
                "Memory usage is critically high. Closing unused apps or restarting your Mac is recommended."
            )

        elif memory.percent >= 80:
            recommendations.append(
                "Memory usage is high. Closing applications you are not using may improve performance."
            )


        # Storage
        disk = shutil.disk_usage("/")

        free_gb = disk.free / (1024 ** 3)

        free_percent = (disk.free / disk.total) * 100

        if free_gb < 15 or free_percent < 10:
            recommendations.append(
                "Storage is running low. Consider deleting large files, emptying the Trash, or moving files to an external drive."
            )


        # Battery
        battery = psutil.sensors_battery()

        if battery:

            if battery.percent <= 20 and not battery.power_plugged:

                recommendations.append(
                    "Battery is low. Consider connecting your charger."
                )


        # Docker
        try:

            result = subprocess.check_output(
                [
                    "docker",
                    "ps",
                    "--format",
                    "{{.Names}}"
                ]
            ).decode()

            running = len(result.splitlines())

            if running >= 5:

                recommendations.append(
                    f"Docker currently has {running} running containers. Stop unused containers to free resources."
                )

        except:
            pass


        if not recommendations:

            return (
                "Everything looks healthy. No maintenance is recommended at the moment."
            )


        return (
            "Recommendations: "
            + " ".join(recommendations)
        )



    def full_status(self):

        return (
            "Here is your Mac status.\n\n"

            f"{self.cpu_usage()}\n"

            f"{self.memory_usage()}\n"

            f"{self.disk_space()}\n"

            f"{self.battery()}\n"

            f"{self.wifi_status()}\n"

            f"{self.docker_status()}\n"

            f"{self.external_drives()}\n\n"

            f"{self.recommendations()}"
        )