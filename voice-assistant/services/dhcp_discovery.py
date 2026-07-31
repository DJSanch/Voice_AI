import subprocess
import re


class DHCPDiscovery:


    def __init__(self):
        pass



    def get_dhcp_devices(self):

        devices = []


        try:

            result = subprocess.check_output(
                [
                    "arp",
                    "-a"
                ]
            ).decode()


            for line in result.splitlines():

                if "incomplete" in line:
                    continue


                if "(" not in line:
                    continue


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


                    devices.append(
                        {
                            "hostname": hostname,
                            "ip": ip,
                            "mac": mac
                        }
                    )


                except:

                    continue


        except Exception as e:

            print(
                "DHCP discovery error:",
                e
            )


        return devices