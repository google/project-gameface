from src.platform import PlatformDetection
from src.platform.generic.generic_virtual_mouse import GenericVirtualMouse
from src.platform.interfaces.camera_interface import CameraInterface
from src.platform.windows.windows_virtual_mouse import WindowsVirtualMouse


class CameraBuilder(PlatformDetection):

    def build(self) -> CameraInterface:
        if self.is_windows():
            return WindowsVirtualMouse()
        else:
            return GenericVirtualMouse()


