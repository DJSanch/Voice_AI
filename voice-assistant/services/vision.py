import Quartz
from PIL import Image


class VisionService:

    def __init__(self, llm, selection):
        self.llm = llm
        self.selection = selection
        self.screenshot_path = "screen.png"


    def capture_screen(self):

        image = Quartz.CGWindowListCreateImage(
            Quartz.CGRectInfinite,
            Quartz.kCGWindowListOptionOnScreenOnly,
            Quartz.kCGNullWindowID,
            Quartz.kCGWindowImageDefault
        )

        width = Quartz.CGImageGetWidth(image)
        height = Quartz.CGImageGetHeight(image)

        provider = Quartz.CGImageGetDataProvider(image)

        data = Quartz.CGDataProviderCopyData(provider)


        img = Image.frombuffer(
            "RGBA",
            (width, height),
            data,
            "raw",
            "BGRA",
            0,
            1
        )


        img = img.convert("RGB")


        img.thumbnail(
            (1280, 1280)
        )


        img.save(
            self.screenshot_path
        )


        return self.screenshot_path



    def analyze_screen(self):

        # Get selected region
        path = self.selection.capture_selection()


        prompt = """
        You are Astra, a Mac AI assistant.

        Analyze the selected screen area.

        Identify:
        - Application name
        - Current task
        - Visible text
        - Errors or warnings
        - What the user should do next

        If it is code:
        - identify the language
        - explain the error
        - suggest a fix

        Keep your answer concise.
        """


        response = self.llm.ask_image(
            prompt,
            path
        )


        if response:
            return response


        return (
            "I captured your screen, "
            "but I could not analyze it."
        )