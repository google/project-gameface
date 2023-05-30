from src.platform import PlatformDetection
from src.platform.generic.generic_virtual_mouse import GenericVirtualMouse
from src.platform.interfaces import mouse_interface
from src.platform.windows.windows_virtual_mouse import WindowsVirtualMouse


class VirtualMouseBuilder(PlatformDetection):

    def build(self) -> mouse_interface:
        if self.is_windows():
            return WindowsVirtualMouse()
        else:
            return GenericVirtualMouse()


