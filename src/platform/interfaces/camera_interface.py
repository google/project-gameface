import concurrent.futures as futures
import logging
import cv2


class CameraMeta(type):

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))


class CameraInterface(metaclass=CameraMeta):

    def __init__(self) -> None:
        self.accepted_backends = ['DSHOW', 'AVFOUNDATION', 'V4L2']
        self.logger = logging.getLogger("ListCamera")

    def open_camera_task(self, i) -> tuple:
        self.logger.debug(f"Try opening camera: {i}")
        accepted_backends = ['DSHOW', 'AVFOUNDATION', 'V4L2']

        try:
            cap = cv2.VideoCapture(i)

            if cap.getBackendName() not in accepted_backends:
                self.logger.debug(f"Camera {i}: {cap.getBackendName()} is not supported")
                return False, i, None

            if cap.get(cv2.CAP_PROP_FRAME_WIDTH) <= 0:
                self.logger.info(f"Camera {i}: frame size error.")
                return False, i, None

            ret, frame = cap.read()
            cv2.waitKey(1)

            if not ret:
                self.logger.debug(f"Camera {i}: No frame returned")
                return False, i, None

            h, w, _ = frame.shape
            self.logger.debug(f"Camera {i}: {cap} height: {h} width: {w}")

            return True, i, cap
        except Exception as e:
            self.logger.debug(f"Camera {i}: not found {e}")
            return False, i, None

    def assign_caps_unblock(self, caps, i):
        ret, _, cap = self.open_camera_task(i)
        if not ret:
            self.logger.debug(f"Camera {i}: Failed to open")
        if cap is not None:
            caps[i] = cap

        else:
            if i in caps:
                del caps[i]

    def assign_caps_queue(self, caps, done_callback: callable, max_search: int):
        for i in range(max_search):

            # block
            ret, _, cap = self.open_camera_task(i)
            if not ret:
                self.logger.debug(f"Camera {i}: Failed to open")
            if cap is not None:
                caps[i] = cap

        done_callback()

    def open_camera(self, caps, i):
        """For swapping camera
        """
        pool = futures.ThreadPoolExecutor(max_workers=1)
        pool.submit(self.assign_caps_unblock, caps, i)
