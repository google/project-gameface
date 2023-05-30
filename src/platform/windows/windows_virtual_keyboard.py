import sys
from src.platform.interfaces.keyboard_interface import KeyboardInterface

if sys.platform == "win32":
    import pydirectinput
    import win32api


class WindowsVirtualKeyboard(KeyboardInterface):

    def __init__(self) -> None:
        # disable lag
        pydirectinput.PAUSE = 0
        pydirectinput.FAILSAFE = False

    def action(self):
        print("Not Implemented yet")

    def destroy(self):
        print("Not Implemented yet")
