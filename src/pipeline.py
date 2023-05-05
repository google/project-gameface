# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging

from src.camera_manager import CameraManager
from src.controllers import Keybinder, MouseController
from src.detectors import FaceMesh


class Pipeline:

    def __init__(self):
        logging.info("Init Pipeline")

    def pipeline_tick(self) -> None:

        frame_rgb = CameraManager().get_raw_frame()

        # Detect landmarks (async) and save in it's buffer
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
