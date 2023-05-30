import sys

from src.platform.interfaces.display_interface import DisplayInterface

if sys.platform == "win32":
    import pydirectinput
    import win32api


class WindowsDisplay(DisplayInterface):

    def __init__(self) -> None:
        super().__init__()

    def size(self) -> tuple[int, int]:
        return pydirectinput.size()

    def get_displays(self):
        return win32api.EnumDisplayMonitors()

    def get_current_display(self):
        print("Not Implemented yet")
