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

from functools import partial

import customtkinter
from PIL import Image

from src.gui.frames.safe_disposable_frame import SafeDisposableFrame

LIGHT_BLUE = "#F9FBFE"
BTN_SIZE = 225, 48


class FrameMenu(SafeDisposableFrame):

    def __init__(self, master, master_callback: callable, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(11, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)
        self.configure(fg_color=LIGHT_BLUE)

        self.master_callback = master_callback

        self.menu_btn_images = {
            "page_home": [
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_home.png").resize(
                        BTN_SIZE, resample=Image.ANTIALIAS),
                    size=BTN_SIZE),
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_home_selected.png"),
                    size=BTN_SIZE)
            ],
            "page_camera": [
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_camera.png"),
                    size=BTN_SIZE),
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_camera_selected.png"),
                    size=BTN_SIZE)
            ],
            "page_cursor": [
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_cursor.png"),
                    size=BTN_SIZE),
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_cursor_selected.png"),
                    size=BTN_SIZE)
            ],
            "page_gestures": [
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_gestures.png"),
                    size=BTN_SIZE),
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_gestures_selected.png"),
                    size=BTN_SIZE)
            ],
            "page_keyboard": [
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_keyboard.png"),
                    size=BTN_SIZE),
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_keyboard_selected.png"),
                    size=BTN_SIZE)
            ]
        }

        self.btns = {}
        self.btns = self.create_tab_btn(self.menu_btn_images)

    def create_tab_btn(self, btns: dict):

        out_dict = {}
        for idx, (k, im_paths) in enumerate(btns.items()):
            btn = customtkinter.CTkButton(master=self,
                                          image=im_paths[0],
                                          anchor="nw",
                                          border_spacing=0,
                                          border_width=0,
                                          hover=False,
                                          corner_radius=0,
                                          text="",
                                          command=partial(self.master_callback,
                                                          command="change_page",
                                                          args={"target": k}))

            btn.grid(row=idx,
                     column=0,
                     padx=(0, 0),
                     pady=0,
                     ipadx=0,
                     ipady=0,
                     sticky="nw")
            btn.configure(fg_color=LIGHT_BLUE, hover=False)
            out_dict[k] = btn
        return out_dict

    def set_tab_active(self, tab_name: str):
        for k, btn in self.btns.items():
            im_normal, im_active = self.menu_btn_images[k]
            if k == tab_name:
                btn.configure(image=im_active)

            else:
                btn.configure(image=im_normal)
