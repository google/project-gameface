from src.platform.interfaces.camera_interface import CameraInterface
import cv2


class WindowsCamera(CameraInterface):

    def open_camera_task(self, i) -> any:
        return super().open_camera_task(cv2.CAP_DSHOW + i)
