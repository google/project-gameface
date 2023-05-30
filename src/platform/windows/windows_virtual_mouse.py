import sys

from src.platform.interfaces.mouse_interface import MouseInterface

if sys.platform == "win32":
    import pydirectinput
    import win32api


class WindowsVirtualMouse(MouseInterface):
    def action(self):
        print("Not Implemented yet")

    def destroy(self):
        print("Not Implemented yet")
