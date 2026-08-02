from plugins.base_plugin import BasePlugin


class VisionPlugin(BasePlugin):

    name = "Vision Plugin"
    version = "1.0"



    def __init__(
        self,
        vision,
        hand_tracking
    ):

        self.vision = vision
        self.hand_tracking = hand_tracking



    def can_handle(self, command):

        text = command.lower()

        return any(
            phrase in text
            for phrase in [
                "what am i looking at",
                "analyze this",
                "read my screen",
                "describe my screen",
                "what am i holding",
                "identify this object"
            ]
        )



    def handle(self, command):

        text = command.lower()


        if (
            "what am i holding" in text
            or "identify this object" in text
        ):

            image = (
                self.hand_tracking
                .capture_hand_region()
            )


            if image:

                return self.vision.analyze_object(
                    image
                )


            return (
                "I couldn't capture the object."
            )


        return (
            self.vision.analyze_screen()
        )