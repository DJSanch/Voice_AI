class DeviceLearning:


    def __init__(
        self,
        memory
    ):

        self.memory = memory



    def remember_device(
        self,
        device,
        name
    ):


        self.memory.add_device(

            mac=device["mac"],

            name=name,

            device_type=device["type"]

        )


        return (
            f"I will remember "
            f"{name} as a "
            f"{device['type']}."
        )