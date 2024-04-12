import concurrent.futures as futures
import logging
import platform

import cv2

if platform.system() == "Windows":
    import pygrabber.dshow_graph

logger = logging.getLogger("ListCamera")


def __open_camera_task(i):
    logger.info(f"Try opening camera: {i}")

    try:
        camera = cv2.VideoCapture(cv2.CAP_DSHOW + i)

        if camera.getBackendName() != "DSHOW":
            logger.info(f"Camera {i}: {camera.getBackendName()} is not supported")
            return (False, i, None)

        if camera.get(cv2.CAP_PROP_FRAME_WIDTH) <= 0:
            logger.info(f"Camera {i}: frame size error.")
            return False, i, None

        ret, frame = camera.read()
        cv2.waitKey(1)

        if not ret:
            logger.info(f"Camera {i}: No frame returned")
            return (False, i, None)

        h, w, _ = frame.shape
        logger.info(f"Camera {i}: {camera} height: {h} width: {w}")

        return (True, i, camera)
    except Exception as e:
        logger.warning(f"Camera {i}: not found {e}")
        return (False, i, None)


def assign_cameras_unblock(cameras, i):
    ret, _, camera = __open_camera_task(i)
    if not ret:
        logger.info(f"Camera {i}: Failed to open")
    if camera is not None:
        cameras[i] = camera

    else:
        if i in cameras:
            del cameras[i]


def assign_cameras_queue(cameras, done_callback: callable, max_search: int):
    for i in range(max_search):
        # block
        ret, _, camera = __open_camera_task(i)
        if not ret:
            logger.info(f"Camera {i}: Failed to open")
        if camera is not None:
            cameras[i] = camera

    done_callback()


def open_camera(cameras, i):
    """For swapping camera"""
    pool = futures.ThreadPoolExecutor(max_workers=1)
    pool.submit(assign_cameras_unblock, cameras, i)


def get_camera_name(i: int) -> str | None:
    if platform.system() == "Windows":
        return str(pygrabber.dshow_graph.FilterGraph().get_input_devices()[i])
    else:
        return None
