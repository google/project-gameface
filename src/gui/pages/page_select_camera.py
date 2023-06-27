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
import tkinter

import customtkinter
from PIL import Image, ImageTk

from src.camera_manager import CameraManager
from src.config_manager import ConfigManager
from src.gui.frames.safe_disposable_frame import SafeDisposableFrame

logger = logging.getLogger("PageSelectCamera")

CANVAS_WIDTH = 320
CANVAS_HEIGHT = 240

MAX_ROWS = 10


class PageSelectCamera(SafeDisposableFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(MAX_ROWS, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Top text
        top_label = customtkinter.CTkLabel(master=self, text="Camera")
        top_label.cget("font").configure(size=24)
        top_label.grid(row=0,
                       column=0,
                       padx=20,
                       pady=20,
                       sticky="nw",
                       columnspan=2)

        # Label
        self.label = customtkinter.CTkLabel(master=self, text="Select a Camera")
        self.label.cget("font").configure(size=16, weight="bold")
        self.label.grid(row=1, column=0, padx=10, pady=(20, 10), sticky="nw")

        # Empty radio buttons
        self.radio_var = tkinter.IntVar(value=0)
        self.prev_radio_value = None
        self.radios = []

        # Camera canvas
        self.placeholder_im = Image.open(
            "assets/images/placeholder.png").resize(
                (CANVAS_WIDTH, CANVAS_HEIGHT))
        self.placeholder_im = ImageTk.PhotoImage(self.placeholder_im)
        self.canvas = tkinter.Canvas(master=self,
                                     width=CANVAS_WIDTH,
                                     height=CANVAS_HEIGHT)
        self.canvas.grid(row=1,
                         column=1,
                         padx=(10, 50),
                         pady=10,
                         sticky="e",
                         rowspan=MAX_ROWS)

        # Set first image.
        self.canvas_im = self.canvas.create_image(0,
                                                  0,
                                                  image=self.placeholder_im,
                                                  anchor=tkinter.NW)
        self.new_photo = None
        self.latest_camera_list = []

    def load_initial_config(self):
        """ Update radio buttons to match CameraManager
        """
        logger.info("Refresh radio buttons")
        for old_radio in self.radios:
            old_radio.destroy()

        new_camera_list = CameraManager().get_camera_list()
        logger.info(f"Get camera list {new_camera_list}")
        radios = []
        for row_i, cam_id in enumerate(new_camera_list):

            radio = customtkinter.CTkRadioButton(master=self,
                                                 text=f"Camera {cam_id}",
                                                 command=self.radiobutton_event,
                                                 variable=self.radio_var,
                                                 value=cam_id)

            radio.grid(row=row_i + 2, column=0, padx=50, pady=10, sticky="w")
            radios.append(radio)

        # Set radio select
        target_id = ConfigManager().config["camera_id"]
        self.radios = radios
        for radio in self.radios:
            if f"Camera {target_id}" == radio.cget("text"):
                radio.select()
                self.prev_radio_value = self.radio_var.get()
                logger.info(f"Set initial camera to {target_id}")
                break

    def radiobutton_event(self):
        # Open new camera.
        new_radio_value = self.radio_var.get()
        if new_radio_value == self.prev_radio_value:
            return
        logger.info(f"Change cameara: {new_radio_value}")
        CameraManager().pick_camera(new_radio_value)
        ConfigManager().set_temp_config("camera_id", new_radio_value)
        ConfigManager().apply_config()
        self.prev_radio_value = new_radio_value

    def page_loop(self):
        if self.is_destroyed:
            return

        if self.is_active:

            frame_rgb = CameraManager().get_raw_frame()
            # Assign ref to avoid garbage collected
            self.new_photo = ImageTk.PhotoImage(
                image=Image.fromarray(frame_rgb).resize((CANVAS_WIDTH,
                                                         CANVAS_HEIGHT)))
            self.canvas.itemconfig(self.canvas_im, image=self.new_photo)
            self.canvas.update()

            self.after(ConfigManager().config["tick_interval_ms"],
                       self.page_loop)

    def enter(self):
        super().enter()
        self.load_initial_config()
        self.after(1, self.page_loop)

    def refresh_profile(self):
        self.load_initial_config()
        new_camera_id = ConfigManager().config["camera_id"]
        CameraManager().pick_camera(new_camera_id)
