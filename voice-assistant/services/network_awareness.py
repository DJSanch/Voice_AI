import subprocess
import psutil
import json
import os
import time
import socket

from mac_vendor_lookup import MacLookup
from services.device_memory import DeviceMemory
from services.device_classifier import DeviceClassifier
from services.mdns_discovery import MDNSDiscovery

class NetworkAwarenessService:

    def __init__(self, tts=None):

        self.device_file = "network_devices.json"

        self.tts = tts

        self.vendor_lookup = MacLookup()

        self.initialize_vendor_database()

        self.memory = DeviceMemory()

        self.classifier = DeviceClassifier()

        self.mdns = MDNSDiscovery()
        
        

    # -----------------------------
    # Vendor database
    # -----------------------------

    def initialize_vendor_database(self):

        try:
            self.vendor_lookup.load_vendors()

        except:

            try:
                self.vendor_lookup.update_vendors()

            except Exception as e:
                print(
                    "Vendor database error:",
                    e
                )


    # -----------------------------
    # Local network
    # -----------------------------

    def get_local_ip(self):

        try:

            return subprocess.check_output(
                [
                    "sh",
                    "-c",
                    "ipconfig getifaddr en0"
                ]
            ).decode().strip()


        except:

            return None



    def get_network_prefix(self):

        ip = self.get_local_ip()


        if not ip:
            return None


        parts = ip.split(".")


        return ".".join(parts[:3]) + "."



    # -----------------------------
    # Network discovery
    # -----------------------------

    def ping_scan(self):

        subnet = self.get_network_prefix()


        if not subnet:
            return


        print(
            "Scanning network..."
        )


        for host in range(1, 255):

            ip = subnet + str(host)


            subprocess.Popen(
                [
                    "ping",
                    "-c",
                    "1",
                    "-W",
                    "100",
                    ip
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )


        time.sleep(3)



    # -----------------------------
    # Device scanner
    # -----------------------------

    def scan_devices(self):

        devices = []

        seen = set()


        try:

            if self.tts:

                self.tts.speak(
                    "Scanning network."
                )


            self.ping_scan()

            mdns_devices = self.mdns.scan()


            arp = subprocess.check_output(
                [
                    "arp",
                    "-a"
                ]
            ).decode()



            for line in arp.splitlines():

                device = self.parse_arp_line(line)


                if not device:
                    continue


                mac = device["mac"]


                if mac in seen:
                    continue


                seen.add(mac)


                devices.append(device)



            # Apply Bonjour names
            devices = self.apply_mdns_names(
                devices,
                mdns_devices
            )



        except Exception as e:

            print(
                "Network scan error:",
                e
            )


        self.save_devices(
            devices
        )


        return devices



    # -----------------------------
    # ARP parser
    # -----------------------------

    def parse_arp_line(self, line):

        if (
            "(" not in line
            or ")" not in line
            or "incomplete" in line
        ):
            return None


        try:

            hostname = line.split()[0]


            ip = (
                line.split("(")[1]
                .split(")")[0]
            )


            mac = (
                line.split("at ")[1]
                .split()[0]
            )


        except:

            return None



        mac = self.normalize_mac(
            mac
        )


        if self.invalid_address(
            ip,
            mac
        ):
            return None



        if hostname == "?":

            hostname = (
                self.resolve_hostname(ip)
                or "Unknown device"
            )


        vendor = self.get_vendor(mac)

        device_type = self.classifier.classify(
            vendor
        )


        return {

            "hostname": hostname,

            "ip": ip,

            "mac": mac,

            "vendor": vendor,

            "type": device_type

        }



    # -----------------------------
    # Filters
    # -----------------------------

    def invalid_address(
        self,
        ip,
        mac
    ):

        return (

            ip.startswith("169.254.")
            or ip.startswith("224.")
            or ip.startswith("239.")
            or ip.endswith(".255")
            or mac == "ff:ff:ff:ff:ff:ff"

        )



    # -----------------------------
    # MAC tools
    # -----------------------------

    def normalize_mac(
        self,
        mac
    ):

        parts = mac.split(":")


        return ":".join(
            part.zfill(2)
            for part in parts
        )



    def get_vendor(
        self,
        mac
    ):

        try:

            return (
                self.vendor_lookup.lookup(mac)
            )


        except:

            return (
                "Unknown manufacturer"
            )



    # -----------------------------
    # Hostname
    # -----------------------------

    def resolve_hostname(
        self,
        ip
    ):

        try:

            return socket.gethostbyaddr(
                ip
            )[0]


        except:

            return None

    

    def apply_mdns_names(
        self,
        devices,
        mdns_devices
    ):

        for device in devices:

            for mdns in mdns_devices:

                if device["ip"] == mdns["ip"]:

                    name = mdns["name"]

                    # Clean Bonjour name
                    name = (
                        name
                        .replace(".local.", "")
                        .replace(".local", "")
                    )


                    device["hostname"] = name


        return devices



    # -----------------------------
    # Device memory
    # -----------------------------

    def save_devices(
        self,
        devices
    ):

        with open(
            self.device_file,
            "w"
        ) as file:

            json.dump(
                devices,
                file,
                indent=4
            )



    def load_devices(self):

        if not os.path.exists(
            self.device_file
        ):

            return []


        with open(
            self.device_file
        ) as file:

            return json.load(file)



    def check_new_devices(self):

        current = self.scan_devices()

        previous = self.load_devices()


        old = {
            d["mac"]
            for d in previous
        }


        return [
            device
            for device in current
            if device["mac"] not in old
        ]



    # -----------------------------
    # Bandwidth
    # -----------------------------

    def bandwidth(self):

        before = psutil.net_io_counters()


        time.sleep(1)


        after = psutil.net_io_counters()


        download = (
            after.bytes_recv -
            before.bytes_recv
        )


        upload = (
            after.bytes_sent -
            before.bytes_sent
        )


        return (

            f"Download speed: "
            f"{download / 1024:.2f} KB/s. "

            f"Upload speed: "
            f"{upload / 1024:.2f} KB/s."

        )



    # -----------------------------
    # Astra report
    # -----------------------------

    def network_report(self):

        devices = self.scan_devices()


        if not devices:

            return (
                "I could not find any devices "
                "on your network."
            )


        report = (
            f"I found {len(devices)} "
            "devices on your network.\n\n"
        )


        for device in devices:


            known_device = self.memory.get_device(
                device["mac"]
            )


            if known_device:

                device_name = known_device["name"]

                device_type = known_device["type"]


            else:

                device_name = (
                    device["hostname"]
                    if device["hostname"] != "Unknown device"
                    else device["vendor"]
                )

                device_type = device["type"]



            report += (
                f"Device: {device_name}\n"
                f"Type: {device_type}\n"
                f"{device['ip']}\n"
                f"Manufacturer: {device['vendor']}\n"
                f"{device['mac']}\n\n"
            )


        report += self.bandwidth()


        return report