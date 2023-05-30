from src.platform import PlatformDetection
from src.platform.generic.generic_display import GenericDisplay
from src.platform.interfaces.display_interface import DisplayInterface
from src.platform.windows.windows_display import WindowsDisplay


class DisplayBuilder(PlatformDetection):

    def __init__(self):
        super().__init__()

    def build(self) -> DisplayInterface:
        if self.is_windows():
            return WindowsDisplay()
        else:
            return GenericDisplay()

