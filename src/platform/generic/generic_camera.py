from src.platform.interfaces.camera_interface import CameraInterface


class GenericCamera(CameraInterface):

    def open_camera_task(self, i) -> any:
        return super().open_camera_task(i)
