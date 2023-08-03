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
import os
import signal

import psutil

import src.utils as utils
from src.singleton_meta import Singleton

logger = logging.getLogger("TaskKiller")


class TaskKiller(metaclass=Singleton):
    """Singleton class for saftly killing the process and free the memory
    """

    def __init__(self):
        logger.info("Intialize TaskKiller singleton")
        self.is_started = False

    def start(self):
        if not self.is_started:
            logging.info("Installing google fonts.")
            utils.install_fonts("assets/fonts")

            # Start singletons
            from src.config_manager import ConfigManager
            ConfigManager().start()

            from src.camera_manager import CameraManager
            CameraManager().start()

            from src.controllers import Keybinder, MouseController
            MouseController().start()
            Keybinder().start()

            from src.detectors import FaceMesh
            FaceMesh().start()

            self.is_started = True

    def exit(self):
        logger.info("Exit program")

        from src.camera_manager import CameraManager
        from src.controllers import Keybinder, MouseController
        from src.detectors import FaceMesh

        CameraManager().destroy()
        MouseController().destroy()
        Keybinder().destroy()
        FaceMesh().destroy()

        utils.remove_fonts("assets/fonts")

        parent = psutil.Process(os.getpid())
        children = parent.children(recursive=True)
        logging.info(f"Kill {parent}, {children}")
        for c in children:
            try:

                c.send_signal(signal.SIGTERM)
            except psutil.NoSuchProcess:
                pass
        parent.send_signal(signal.SIGTERM)
        exit()
