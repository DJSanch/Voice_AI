class DeviceClassifier:


    def classify(self, vendor):

        vendor = vendor.lower()


        # Apple
        if any(
            name in vendor
            for name in [
                "apple",
                "cloud network technology",
                "foxconn",
                "hon hai",
                "compal"
            ]
        ):
            return "Apple Device"


        # Amazon
        if any(
            name in vendor
            for name in [
                "amazon",
                "ring"
            ]
        ):
            return "Smart Home Device"


        # Google
        if "google" in vendor:
            return "Google Device"


        # Samsung
        if "samsung" in vendor:
            return "Samsung Device"


        # Microsoft
        if "microsoft" in vendor:
            return "Windows Device"


        # TP-Link
        if any(
            name in vendor
            for name in [
                "tp-link",
                "tplink"
            ]
        ):
            return "Network Equipment"


        # Intel
        if "intel" in vendor:
            return "Computer Hardware"


        # Raspberry Pi
        if "raspberry" in vendor:
            return "IoT Device"


        return "Unknown Device"