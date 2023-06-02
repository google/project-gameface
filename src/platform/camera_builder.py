from src.platform import PlatformDetection
from src.platform.generic.generic_camera import GenericCamera
from src.platform.interfaces.camera_interface import CameraInterface
from src.platform.windows.windows_camera import WindowsCamera


class CameraBuilder(PlatformDetection):

    def __init__(self):
        super().__init__()

    def build(self) -> CameraInterface:
        if self.is_windows():
            return WindowsCamera()

        return GenericCamera()


