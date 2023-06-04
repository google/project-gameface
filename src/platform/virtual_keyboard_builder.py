from src.platform import PlatformDetection
from src.platform.darwin.darwin_virtual_keyboard import DarwinVirtualKeyboard
from src.platform.generic.generic_virtual_keyboard import GenericVirtualKeyboard
from src.platform.interfaces import keyboard_interface
from src.platform.windows.windows_virtual_keyboard import WindowsVirtualKeyboard


class VirtualKeyboardBuilder(PlatformDetection):
    def __init__(self):
        super().__init__()

    def build(self) -> keyboard_interface:
        if self.is_windows():
            return WindowsVirtualKeyboard()
        elif self.is_darwin():
            return DarwinVirtualKeyboard()

        return GenericVirtualKeyboard()
