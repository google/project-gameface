from functools import partial

import customtkinter
from PIL import Image

from src.config_manager import ConfigManager
from src.gui.pages import (
    PageSelectCamera,
    PageCursor,
    PageSelectGestures,
    PageKeyboard,
    PageAbout,
)
from src.gui.frames.safe_disposable_frame import SafeDisposableFrame

LIGHT_BLUE = "#F9FBFE"
BTN_SIZE = 225, 48
PROF_DROP_SIZE = 220, 40


class FrameMenu(SafeDisposableFrame):
    def __init__(self, master, master_callback: callable, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_propagate(False)
        self.configure(fg_color=LIGHT_BLUE)

        self.master_callback = master_callback

        self.menu_btn_images = {
            PageSelectCamera.__name__: [
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_camera.png"), size=BTN_SIZE
                ),
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_camera_selected.png"),
                    size=BTN_SIZE,
                ),
            ],
            PageCursor.__name__: [
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_cursor.png"), size=BTN_SIZE
                ),
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_cursor_selected.png"),
                    size=BTN_SIZE,
                ),
            ],
            PageSelectGestures.__name__: [
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_gestures.png"), size=BTN_SIZE
                ),
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_gestures_selected.png"),
                    size=BTN_SIZE,
                ),
            ],
            PageKeyboard.__name__: [
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_keyboard.png"), size=BTN_SIZE
                ),
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_keyboard_selected.png"),
                    size=BTN_SIZE,
                ),
            ],
            PageAbout.__name__: [
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_about.png"), size=BTN_SIZE
                ),
                customtkinter.CTkImage(
                    Image.open("assets/images/menu_btn_about_selected.png"),
                    size=BTN_SIZE,
                ),
            ],
        }

        # Profile button
        prof_drop = customtkinter.CTkImage(
            Image.open("assets/images/prof_drop_head.png"), size=PROF_DROP_SIZE
        )
        profile_btn = customtkinter.CTkLabel(
            master=self,
            textvariable=ConfigManager().current_profile_name,
            image=prof_drop,
            height=42,
            compound="center",
            anchor="w",
            cursor="hand2",
        )
        profile_btn.bind(
            "<Button-1>", partial(self.master_callback, "show_profile_switcher")
        )

        profile_btn.grid(
            row=0,
            column=0,
            padx=35,
            pady=10,
            ipadx=0,
            ipady=0,
            sticky="nw",
            columnspan=1,
            rowspan=1,
        )

        self.buttons = {}
        self.buttons = self.create_tab_btn(self.menu_btn_images, offset=1)
        self.set_tab_active(PageSelectCamera.__name__)

    def create_tab_btn(self, btns: dict, offset):
        out_dict = {}
        for idx, (k, im_paths) in enumerate(btns.items()):
            btn = customtkinter.CTkButton(
                master=self,
                image=im_paths[0],
                anchor="nw",
                border_spacing=0,
                border_width=0,
                hover=False,
                corner_radius=0,
                text="",
                command=partial(
                    self.master_callback,
                    function_name="change_page",
                    args={"target": k},
                ),
            )

            btn.grid(
                row=idx + offset,
                column=0,
                padx=(0, 0),
                pady=0,
                ipadx=0,
                ipady=0,
                sticky="nw",
            )
            btn.configure(fg_color=LIGHT_BLUE, hover=False)
            out_dict[k] = btn
        return out_dict

    def set_tab_active(self, tab_name: str):
        for k, btn in self.buttons.items():
            im_normal, im_active = self.menu_btn_images[k]
            if k == tab_name:
                btn.configure(image=im_active)

            else:
                btn.configure(image=im_normal)
