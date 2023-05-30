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
import sys

import cv2

logger = logging.getLogger("ListCamera")


def __open_camera_task(i):

    logger.info(f"Try openning camera: {i}")

    try:
        cam_offset = 0
        if sys.platform == "win32":
            cam_offset = cv2.CAP_DSHOW
        cap = cv2.VideoCapture(cam_offset + i)
        backend_name = cap.getBackendName()
        if cap.getBackendName() != "DSHOW" and cap.getBackendName() != "AVFOUNDATION":
            logger.info(f"Camera {i}: {cap.getBackendName()} is not supported")
            return (False, i, None)
        frame_width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        if cap.get(cv2.CAP_PROP_FRAME_WIDTH) <= 0:
            logger.info(f"Camera {i}: frame size error.")
            return False, i, None

        ret, frame = cap.read()
        cv2.waitKey(1)

        if not ret:
            logger.info(f"Camera {i}: No frame returned")
            return (False, i, None)

        h, w, _ = frame.shape
        logger.info(f"Camera {i}: {cap} height: {h} width: {w}")

        return (True, i, cap)
    except Exception as e:
        logger.warning(f"Camera {i}: not found {e}")
        return (False, i, None)


def assign_caps_unblock(caps, i):
    ret, _, cap = __open_camera_task(i)
    if not ret:
        logger.info(f"Camera {i}: Failed to open")
    if cap is not None:
        caps[i] = cap

    else:
        if i in caps:
            del caps[i]


def assign_caps_queue(caps, done_callback: callable, max_search: int):

    for i in range(max_search):

        # block
        ret, _, cap = __open_camera_task(i)
        if not ret:
            logger.info(f"Camera {i}: Failed to open")
        if cap is not None:
            caps[i] = cap

    done_callback()


def open_camera(caps, i):
    """For swapping camera
    """
    pool = futures.ThreadPoolExecutor(max_workers=1)
    pool.submit(assign_caps_unblock, caps, i)
