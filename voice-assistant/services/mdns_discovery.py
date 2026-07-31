from zeroconf import Zeroconf, ServiceBrowser
import time


SERVICE_TYPES = [
    "_device-info._tcp.local.",
    "_airplay._tcp.local.",
    "_http._tcp.local.",
    "_ssh._tcp.local.",
    "_smb._tcp.local.",
    "_workstation._tcp.local.",
]


class MDNSListener:


    def __init__(self):

        self.devices = []



    def add_service(
        self,
        zeroconf,
        service_type,
        name
    ):

        try:

            info = zeroconf.get_service_info(
                service_type,
                name
            )


            if not info:
                return


            addresses = info.parsed_addresses()


            if not addresses:
                return



            device = {

                "name": name,

                "ip": addresses[0]

            }



            if device not in self.devices:

                self.devices.append(
                    device
                )


        except Exception as e:

            print(
                "mDNS error:",
                e
            )



    def remove_service(
        self,
        zeroconf,
        service_type,
        name
    ):

        pass



    def update_service(
        self,
        zeroconf,
        service_type,
        name
    ):

        pass




class MDNSDiscovery:


    def scan(self):

        zeroconf = Zeroconf()

        listener = MDNSListener()


        browsers = []


        try:

            for service in SERVICE_TYPES:

                browsers.append(
                    ServiceBrowser(
                        zeroconf,
                        service,
                        listener
                    )
                )


            time.sleep(5)



        finally:

            zeroconf.close()



        return listener.devices