from typing import List

from src.platform.interfaces.display_interface import DisplayInterface


class GenericDisplay(DisplayInterface):

    def __init__(self) -> object:
        print("Generic Display Interface Used")

    def get_displays(self):
        print("Not Implemented yet")
        return []

    def get_current_display(self):
        print("Not Implemented yet")

    def size(self) -> list[int]:
        return [110, 100]
