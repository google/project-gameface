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

import concurrent.futures as futures
import logging
import threading
import time
from threading import Thread

import cv2
import numpy as np
import numpy.typing as npt
from PIL import Image

import src.utils as utils
from src.config_manager import ConfigManager
from src.controllers import MouseController
from src.singleton_meta import Singleton

MAX_SEARCH_CAMS = 5

logger = logging.getLogger("CameraManager")


def add_overlay(background, overlay, x, y, width, height):

    background_section = background[y:y + height, x:x + width]
    overlay_section = overlay[y:y + height, x:x + width]
    background[y:y + height,
               x:x + width] = cv2.addWeighted(background_section, 0.3,
                                              overlay_section, 0.7, 0)
    return background


class CameraManager(metaclass=Singleton):

    def __init__(self):
        logger.info("Intialize CameraManager singleton")
        self.thread_cameras = None

        # Load placeholder image
        self.placeholder_im = Image.open("assets/images/placeholder.png")
        self.placeholder_im = np.array(self.placeholder_im.convert('RGB'))

        # Overlays
        self.overlay_active = cv2.cvtColor(
            cv2.imread("assets/images/overlays/active.png",
                       cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGB)
        self.overlay_disabled = cv2.cvtColor(
            cv2.imread("assets/images/overlays/disabled.png",
                       cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGB)
        self.overlay_face_not_detected = cv2.cvtColor(
            cv2.imread("assets/images/overlays/face_not_detected.png",
                       cv2.IMREAD_UNCHANGED), cv2.COLOR_BGRA2RGB)

        # Use dict for pass as reference
        self.frame_buffers = {
            "raw": self.placeholder_im,
            "debug": self.placeholder_im
        }
        self.is_active = False
        self.is_destroyed = False

    def start(self):
        if not self.is_active:
            logger.info("Start CameraManager singleton")
            self.thread_cameras = ThreadCameras(self.frame_buffers)
            self.is_active = True

    def get_camera_list(self) -> list[int]:
        if not self.is_active:
            return []
        ret_caps = list(self.thread_cameras.caps.keys())

        return sorted(ret_caps)

    def get_current_camera_id(self) -> int:
        if not self.is_active:
            return None
        else:
            return self.thread_cameras.curr_id

    def pick_camera(self, camera_id: int) -> None:
        logger.info(f"Swapping to camera id: {camera_id}")
        # Assign to ref
        self.frame_buffers["raw"] = self.placeholder_im
        self.frame_buffers["debug"] = self.placeholder_im
        self.thread_cameras.pick_camera(camera_id)

    def get_raw_frame(self):
        return self.frame_buffers["raw"].copy()

    def get_debug_frame(self):
        return self.frame_buffers["debug"]

    def put_debug_frame(self, frame_debug: npt.ArrayLike) -> None:
        self.frame_buffers["debug"] = frame_debug

    def leave(self):
        if self.thread_cameras is not None:
            self.thread_cameras.leave()

    def destroy(self):
        self.is_destroyed = True
        if self.thread_cameras is not None:
            self.thread_cameras.destroy()

    def draw_overlay(self, track_loc):
        if not self.is_active:
            return

        self.frame_buffers["debug"] = self.frame_buffers["raw"].copy()

        # Disabled
        if not MouseController().is_active.get():
            self.frame_buffers["debug"] = add_overlay(
                self.frame_buffers["debug"], self.overlay_disabled, 0, 0, 640,
                108)
            return

        # Face not detected
        if (track_loc is None):
            self.frame_buffers["debug"] = add_overlay(
                self.frame_buffers["debug"], self.overlay_face_not_detected, 0,
                0, 640, 108)

            return

        # Active

        if ConfigManager().config["use_transformation_matrix"]:
            cx = ConfigManager().config["fix_width"] // 2
            cy = ConfigManager().config["fix_height"] // 2
            cv2.line(self.frame_buffers["debug"], (cx, cy),
                     (int(track_loc[0]), int(track_loc[1])), (0, 255, 0), 3)

            cv2.circle(self.frame_buffers["debug"],
                       (int(track_loc[0]), int(track_loc[1])), 6, (255, 0, 0),
                       -1)

        else:
            cv2.circle(self.frame_buffers["debug"],
                       (int(track_loc[0]), int(track_loc[1])), 4,
                       (255, 255, 255), -1)


# ---------------------------------------------------------------------------- #
#                                 THREAD CAMERA                                #
# ---------------------------------------------------------------------------- #


class ThreadCameras():

    def __init__(self, frame_buffers: dict):
        logger.info("Intializing Threadcamera")
        self.lock = threading.Lock()
        self.pool = futures.ThreadPoolExecutor(max_workers=8)
        self.stop_flag = threading.Event()
        self.assign_done_flag = threading.Event()
        self.frame_buffers = frame_buffers

        # Open all cameras
        self.caps = {}

        self.assign_exe = Thread(target=utils.assign_caps_queue,
                                 args=(self.caps, self.assign_done,
                                       MAX_SEARCH_CAMS),
                                 daemon=True)
        self.assign_exe.start()
        # Decide what camera to use
        self.curr_id = None  #ConfigManager().config["camera_id"]
        logger.info(f"Found default camera_id {self.curr_id}")

        self.loop_exe = Thread(target=self.read_camera_loop,
                               args=(self.stop_flag,),
                               daemon=True)
        self.loop_exe.start()

    def assign_done(self):
        """Set default camera after assign_caps is done
        """
        logger.info(f"Assign cameras completed. Found {self.caps}")

        init_id = ConfigManager().config["camera_id"]

        # pick first camera available if camera in config not found
        if init_id not in self.caps:
            self.curr_id = list(self.caps.keys())[0]
        else:
            self.curr_id = init_id

        logger.info(f"Try to use camera {self.curr_id}")
        self.pick_camera(self.curr_id)
        self.assign_done_flag.set()

    def pick_camera(self, new_id: int) -> None:
        """Open only one camera and release all others.

        Args:
            new_id (int): camera id to open
        """

        logger.info(f"Pick camera {new_id}, Releasing others...")

        if new_id not in self.caps:
            logger.error(f"Camera {new_id} not found")
            return

        for cam_id, _ in self.caps.items():
            if cam_id == new_id:
                if self.caps[new_id] is not None:
                    continue
                utils.open_camera(self.caps, cam_id)
            else:
                if self.caps[cam_id] is not None:
                    self.caps[cam_id].release()
                self.caps[cam_id] = None

        self.curr_id = new_id

    def release_all_cameras(self):
        if self.caps is not None:
            for cam_id, _ in self.caps.items():
                if self.caps[cam_id] is not None:
                    self.caps[cam_id].release()
                self.caps[cam_id] = None

    def read_camera_loop(self, stop_flag) -> None:
        logger.info("Threadcamera main_loop started.")

        while not stop_flag.is_set():
            if self.curr_id is None:
                time.sleep(1)
                continue

            if not self.assign_done_flag.is_set():
                time.sleep(1)
                continue

            if (self.curr_id in self.caps) and (self.caps[self.curr_id]
                                                is not None):
                ret, frame = self.caps[self.curr_id].read()
                cv2.waitKey(1)
                if not ret:
                    logger.error("No frame returned")
                    time.sleep(1)
                    continue
            else:
                time.sleep(1)
                continue

            frame.flags.writeable = False
            h, w, _ = frame.shape

            # Trim image
            if h != ConfigManager().config["fix_height"] or w != ConfigManager(
            ).config["fix_width"]:
                target_width = int(h * 4 / 3)
                if w > target_width:
                    trim_width = w - target_width
                    trim_left = trim_width // 2
                    trim_right = trim_width - trim_left
                    frame = frame[:, trim_left:-trim_right, :]
                frame = cv2.resize(frame,
                                   (ConfigManager().config["fix_width"],
                                    ConfigManager().config["fix_height"]))
            frame = cv2.flip(frame, 1)
            self.frame_buffers["raw"] = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        return

    def leave(self):
        pass

    def destroy(self):
        logger.info("Destroying Threadcamera")
        self.stop_flag.set()
        self.assign_exe.join()
        self.loop_exe.join()

        # Release all cameras
        self.release_all_cameras()
        self.frame_buffers = None
        self.caps = None

        logger.info("Threadcamera destroyed")
