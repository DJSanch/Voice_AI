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
    
    def analyze_object(self, image_path):

        vision_prompt = """
        You are Astra, a helpful AI assistant.

        Look carefully at the object the person is holding.

        Describe the object in one short sentence.

        Include:
        - The object name
        - Color
        - Visible Text
        - Shape or visible features
        - Any recognizable details

        If you are uncertain, say:
        "I am not completely sure, but it looks like..."
        """
        

        description = self.llm.ask_image(
            vision_prompt,
            image_path
        )


        reasoning_prompt = f"""

        {description}

        Give:
        - Object name
        - Short explanation
        - suggest other brands related to the object:
            if the brand suggest that it does not support the object make sure to rule it out and recommend that it is this kind of object.
          

        Keep it conversational.
        """


        answer = self.llm.ask(
            reasoning_prompt
        )


        return answer