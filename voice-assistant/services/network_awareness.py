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
from services.device_fingerprint import DeviceFingerprint
from services.dhcp_discovery import DHCPDiscovery
from services.device_learning import DeviceLearning
from concurrent.futures import ThreadPoolExecutor, as_completed

class NetworkAwarenessService:

    def __init__(self, tts=None):

        self.device_file = "data/network_devices.json"

        self.memory_file = "data/known_devices.json"

        self.my_device = self.get_my_mac()

        self.tts = tts

        self.vendor_lookup = MacLookup()

        self.initialize_vendor_database()

        self.memory = DeviceMemory()

        self.learning = DeviceLearning(
            self.memory
        )

        self.classifier = DeviceClassifier()

        self.mdns = MDNSDiscovery()

        self.fingerprint = DeviceFingerprint()

        self.dhcp = DHCPDiscovery()
        
        

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
        
    
    # -----------------------------
    # Detect Astra's MacBook
    # -----------------------------

    def get_my_mac(self):

        try:

            result = subprocess.check_output(
                [
                    "sh",
                    "-c",
                    "networksetup -getmacaddress en0"
                ]
            ).decode().strip()


            # Example:
            # Wi-Fi MAC Address: aa:bb:cc:dd:ee:ff

            mac = result.split()[-1]


            return self.normalize_mac(mac)


        except Exception as e:

            print(
                "Could not detect local MAC:",
                e
            )

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

        hosts = [
            subnet + str(i)
            for i in range(1, 255)
        ]

        total = len(hosts)
        completed = 0

        print("Scanning network...")

        def ping(ip):

            subprocess.run(
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

            return ip


        with ThreadPoolExecutor(
            max_workers=50
        ) as executor:

            futures = [
                executor.submit(
                    ping,
                    ip
                )
                for ip in hosts
            ]


            for future in as_completed(futures):

                completed += 1

                self.show_progress(
                    completed,
                    total
                )


        print("\nScan complete.")
    

    def show_progress(self, current, total):

        bar_length = 30

        percent = current / total

        filled = int(bar_length * percent)

        bar = "█" * filled + "░" * (
            bar_length - filled
        )

        print(
            f"\rScanning network [{bar}] {percent*100:.0f}%",
            end="",
            flush=True
        )


    # -----------------------------
    # Device scanner
    # -----------------------------

    def scan_devices(self):

        devices = []

        seen = set()

        try:

            self.ping_scan()

            mdns_devices = self.mdns.scan()

            dhcp_devices = self.dhcp.get_dhcp_devices()


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

            devices = self.apply_dhcp_names(
                devices,
                dhcp_devices
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

        device_owner = self.identify_device(mac)

        fingerprint = self.fingerprint.fingerprint(
            ip,
            vendor
        )


        device_type = fingerprint["fingerprint"]


        return {

            "hostname": hostname,

            "ip": ip,

            "mac": mac,

            "vendor": vendor,

            "type": device_type,

            "services": fingerprint["services"],

            "confidence": fingerprint["confidence"],

            "owner": device_owner

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


    # -----------------------------
    # Identify owner
    # -----------------------------
    
    def identify_device(
        self,
        mac
    ):

        if not self.my_device:
            return None


        if (
            mac.lower()
            ==
            self.my_device.lower()
        ):

            return "My MacBook"


        return None



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
    
    def apply_dhcp_names(
        self,
        devices,
        dhcp_devices
    ):

        for device in devices:

            for dhcp in dhcp_devices:


                if device["mac"].lower() == dhcp["mac"].lower():


                    hostname = dhcp["hostname"]


                    if hostname != "?":

                        device["hostname"] = hostname


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


        previous_macs = {
            device["mac"]
            for device in previous
        }


        new_devices = [
            device
            for device in current
            if device["mac"] not in previous_macs
        ]


        return new_devices



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
    

    def monitor_new_devices(self):

        previous = {
            d["mac"]
            for d in self.load_devices()
        }

        while True:

            current = self.scan_devices()

            current_macs = {
                d["mac"]
                for d in current
            }

            new = current_macs - previous

            for device in current:

                if device["mac"] in new:

                    name = (
                        device["hostname"]
                        if device["hostname"] not in ["", "?", "Unknown device"]
                        else device["vendor"]
                    )

                    message = f"New device detected: {name}"

                    print(message)

                    if self.tts:
                        self.tts.speak(message)

            previous = current_macs

            time.sleep(30)
        
    
    def detect_new_devices(self):

        current = self.scan_devices()

        previous = self.load_devices()


        previous_macs = {
            device["mac"]
            for device in previous
        }


        new_devices = [
            device
            for device in current
            if device["mac"] not in previous_macs
        ]


        return new_devices



    # -----------------------------
    # Astra report
    # -----------------------------
    def network_report(self):

        if self.tts:
            self.tts.speak(
                "Scanning network."
            )

        # Scan and detect changes
        new_devices = self.detect_new_devices()

        devices = self.load_devices()


        if not devices:
            return (
                "I could not find any devices "
                "on your network."
            )


        report = (
            f"I found {len(devices)} "
            "devices on your network.\n\n"
        )


        # New device notification
        if new_devices:

            report += "New devices detected:\n"

            for device in new_devices:

                name = (
                    device["hostname"]
                    if device["hostname"] not in [
                        "",
                        "?",
                        "Unknown device"
                    ]
                    else device["vendor"]
                )

                report += (
                    f"- {name} "
                    f"({device['ip']})\n"
                )


            report += "\n"


        # Device details
        for device in devices:

            if device.get("owner"):

                device_name = device["owner"]
                device_type = "Personal Computer"


            else:

                known_device = self.memory.get_device(
                    device["mac"]
                )


                if known_device:

                    device_name = known_device["name"]
                    device_type = known_device["type"]


                elif device["hostname"] not in [
                    "?",
                    "Unknown device",
                    ""
                ]:

                    device_name = device["hostname"]
                    device_type = device["type"]


                else:

                    device_name = device["vendor"]
                    device_type = device["type"]



            report += (

                f"Device: {device_name}\n"
                f"Type: {device_type}\n"
                f"IP: {device['ip']}\n"
                f"Manufacturer: {device['vendor']}\n"
                f"Services: "
                f"{', '.join(device.get('services', [])) or 'None'}\n"
                f"Confidence: "
                f"{device.get('confidence', 0)}%\n"
                f"MAC: {device['mac']}\n\n"

            )


        report += self.bandwidth()


        return report