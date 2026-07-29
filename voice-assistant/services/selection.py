import subprocess
import os
from PIL import ImageGrab

class SelectionService:

    def __init__(self):
        self.selection_path = "selection.png"


    def capture_selection(self):

        # Use native macOS screenshot selection
        subprocess.run(
            [
                "screencapture",
                "-i",
                self.selection_path
            ]
        )


        if os.path.exists(self.selection_path):

            return self.selection_path


        return None

    
    def capture_region(self, region):

        image = ImageGrab.grab(
            bbox=region
        )

        path = "selection.png"

        image.save(path)

        return path