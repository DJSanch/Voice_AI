import socket


class DeviceFingerprint:


    def __init__(self):

        self.ports = {

            22: "SSH",
            80: "HTTP",
            443: "HTTPS",
            445: "SMB",
            3389: "Remote Desktop",
            5000: "AirPlay",
            7000: "AirPlay",
            5900: "VNC",
            62078: "Apple Device Sync"

        }



    def scan_ports(
        self,
        ip
    ):

        services = []


        for port, name in self.ports.items():

            try:

                sock = socket.socket(
                    socket.AF_INET,
                    socket.SOCK_STREAM
                )

                sock.settimeout(
                    0.3
                )


                result = sock.connect_ex(
                    (
                        ip,
                        port
                    )
                )


                if result == 0:

                    services.append(
                        name
                    )


                sock.close()


            except:

                continue



        return services



    def identify_device(
        self,
        vendor,
        services
    ):


        if (
            "SMB" in services
            and "Remote Desktop" in services
        ):

            return (
                "Windows Computer",
                90
            )


        if (
            "AirPlay" in services
        ):

            return (
                "Apple Device",
                85
            )


        if (
            "SSH" in services
        ):

            return (
                "Linux/Mac Device",
                75
            )


        if (
            "HTTP" in services
            or "HTTPS" in services
        ):

            return (
                "Network Device",
                60
            )


        if "Amazon" in vendor:

            return (
                "Amazon Smart Device",
                80
            )


        return (
            "Unknown Device",
            20
        )



    def fingerprint(
        self,
        ip,
        vendor
    ):

        services = self.scan_ports(
            ip
        )


        device_type, confidence = self.identify_device(
            vendor,
            services
        )


        return {

            "services": services,

            "fingerprint": device_type,

            "confidence": confidence

        }