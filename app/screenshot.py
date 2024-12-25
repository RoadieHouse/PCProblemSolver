# app/screenshot.py
from PIL import ImageGrab
import tempfile
import os

def take_screenshot():
    """Take a screenshot and return the path."""
    temp_dir = tempfile.gettempdir()
    screenshot_path = os.path.join(temp_dir, "screenshot.png")
    screenshot = ImageGrab.grab()
    screenshot.save(screenshot_path)
    return screenshot_path
