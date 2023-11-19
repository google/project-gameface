import logging

from src.camera_manager import CameraManager
from src.controllers import Keybinder, MouseController
from src.detectors import FaceMesh


class Pipeline:

    def __init__(self):
        logging.info("Init Pipeline")

    def pipeline_tick(self) -> None:

        frame_rgb = CameraManager().get_raw_frame()

        # Detect landmarks (async) and save in its buffer
        FaceMesh().detect_frame(frame_rgb)

        # Get facial landmarks
        landmarks = FaceMesh().get_landmarks()
        if (landmarks is None):
            CameraManager().draw_overlay(track_loc=None)
            return

        # Control mouse position
        track_loc = FaceMesh().get_track_loc()
        MouseController().act(track_loc)

        # Control keyboard
        blendshape_values = FaceMesh().get_blendshapes()
        Keybinder().act(blendshape_values)

        # Draw frame overlay
        CameraManager().draw_overlay(track_loc)
