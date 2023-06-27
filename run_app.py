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
import sys
import os
import customtkinter

import src.gui as gui
from src.task_killer import TaskKiller
from src.pipeline import Pipeline

FORMAT = "%(asctime)s %(levelname)s %(name)s: %(funcName)s: %(message)s"

if not os.path.isdir("C:\\Temp\\"):
    os.mkdir("C:\\Temp\\")

logging.basicConfig(
    format=FORMAT,
    level=logging.INFO,
    handlers=[
        logging.FileHandler("C:\Temp\log.txt", mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
)


class MainApp(gui.MainGui, Pipeline):
    def __init__(self, tk_root):
        super().__init__(tk_root)
        # Wait for window drawing.
        self.tk_root.wm_protocol("WM_DELETE_WINDOW", self.close_all)

        self.is_active = True

        # Enter loop
        self.tk_root.after(1, self.anim_loop)

    def anim_loop(self):
        try:
            if self.is_active:
                # Run detectors and controllers.
                self.pipeline_tick()
                self.tk_root.after(1, self.anim_loop)
        except Exception as e:
            logging.critical(e, exc_info=e)

    def close_all(self):
        logging.info("Close all")
        self.is_active = False
        # Completely clost this process
        TaskKiller().exit()


if __name__ == "__main__":
    tk_root = customtkinter.CTk()

    logging.info("Starting main app.")
    TaskKiller().start()

    main_app = MainApp(tk_root)
    main_app.tk_root.mainloop()

    main_app = None
