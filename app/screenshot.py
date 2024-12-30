import tempfile
import os
from PIL import ImageGrab


import time

def take_screenshot() -> str:
    """
    Take a screenshot and return the path to the saved image.
        str: The file path of the saved screenshot.
    """
    # Get the temporary directory
    temp_dir = tempfile.gettempdir()
    # Define the path for the screenshot
    screenshot_path = os.path.join(temp_dir, "screenshot.png")
    # Take the screenshot
    screenshot = ImageGrab.grab()
    # Save the screenshot to the defined path
    screenshot.save(screenshot_path)
    # Return the path of the saved screenshot
    return screenshot_path
