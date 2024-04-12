import logging
import time
from typing import Any

import mediapipe as mp
import numpy as np
import numpy.typing as npt
from mediapipe.framework.formats.landmark_pb2 import NormalizedLandmark
from mediapipe.python._framework_bindings import image as mediapipe_image
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import FaceLandmarkerResult
from numpy import ndarray, dtype

import src.utils as utils
from src.config_manager import ConfigManager
from src.singleton_meta import Singleton

logger = logging.getLogger("FaceMesh")

MP_TASK_FILE = "assets/task/face_landmarker_with_blendshapes.task"

BLENDS_MAX_BUFFER = 100
N_SHAPES = 52
np.set_printoptions(precision=2, suppress=True)


class FaceMesh(metaclass=Singleton):
    def __init__(self):
        self.smooth_kernel = None
        logger.info("Initialize FaceMesh singleton")
        self.mp_landmarks = None
        self.tracking_location = None
        self.blendshapes_buffer = np.zeros([BLENDS_MAX_BUFFER, N_SHAPES])
        self.smooth_blendshapes = None
        self.model = None
        self.latest_time_ms = 0
        self.is_started = False

    def start(self):
        if not self.is_started:
            logger.info("Start FaceMesh singleton")
            # In Windows, needs to open buffer directly
            with open(MP_TASK_FILE, mode="rb") as f:
                f_buffer = f.read()
            base_options = python.BaseOptions(model_asset_buffer=f_buffer)
            options = vision.FaceLandmarkerOptions(
                base_options=base_options,
                output_face_blendshapes=True,
                output_facial_transformation_matrixes=True,
                running_mode=mp.tasks.vision.RunningMode.LIVE_STREAM,
                num_faces=1,
                result_callback=self.mp_callback,
            )
            self.model = vision.FaceLandmarker.create_from_options(options)

            self.calc_smooth_kernel()

    def calc_smooth_kernel(self):
        self.smooth_kernel = utils.calc_smooth_kernel(
            ConfigManager().config["shape_smooth"]
        )

    def calculate_tracking_location(
        self, mp_result, use_transformation_matrix=False
    ) -> ndarray[Any, dtype[Any]]:
        screen_w = ConfigManager().config["fix_width"]
        screen_h = ConfigManager().config["fix_height"]
        landmarks = mp_result.face_landmarks[0]

        if use_transformation_matrix:
            M = mp_result.facial_transformation_matrixes[0]
            U, _, V = np.linalg.svd(M[:3, :3])
            R = U @ V

            res = R @ np.array([0, 0, 1])

            x_pixel = (res[0] / 1) * 0.3
            y_pixel = (res[1] / 1) * 0.3

            x_pixel = screen_w / 2 + (x_pixel * screen_w / 2)
            y_pixel = screen_h / 2 - (y_pixel * screen_h / 2)

        else:
            axs = []
            ays = []

            for p in ConfigManager().config["tracking_vert_idxs"]:
                px = landmarks[p].x * screen_w
                py = landmarks[p].y * screen_h
                axs.append(px)
                ays.append(py)

            x_pixel = np.mean(axs)
            y_pixel = np.mean(ays)

        return np.array([x_pixel, y_pixel], np.float32)

    def mp_callback(
        self,
        mp_result: FaceLandmarkerResult,
        output_image: mediapipe_image.Image,
        timestamp_ms: int,
    ) -> None:
        if len(mp_result.face_landmarks) >= 1 and len(mp_result.face_blendshapes) >= 1:
            self.mp_landmarks = mp_result.face_landmarks[0]
            # Point for moving pointer
            self.tracking_location = self.calculate_tracking_location(
                mp_result,
                use_transformation_matrix=ConfigManager().config[
                    "use_transformation_matrix"
                ],
            )
            self.blendshapes_buffer = np.roll(self.blendshapes_buffer, shift=-1, axis=0)

            self.blendshapes_buffer[-1] = np.array(
                [b.score for b in mp_result.face_blendshapes[0]]
            )
            self.smooth_blendshapes = utils.apply_smoothing(
                self.blendshapes_buffer, self.smooth_kernel
            )

        else:
            self.mp_landmarks = None
            self.tracking_location = None

    def detect_frame(self, frame_np: npt.ArrayLike):
        t_ms = int(time.time() * 1000)
        if t_ms <= self.latest_time_ms:
            return

        frame_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_np)
        self.model.detect_async(frame_mp, t_ms)
        self.latest_time_ms = t_ms

    def get_landmarks(self) -> list[NormalizedLandmark]:
        return self.mp_landmarks

    def get_tracking_location(self) -> ndarray:
        return self.tracking_location

    def get_blendshapes(self) -> npt.ArrayLike:
        return self.smooth_blendshapes

    def destroy(self):
        if self.model is not None:
            self.model.close()
        self.model = None
        self.mp_landmarks = None
        self.blendshapes_buffer = None
