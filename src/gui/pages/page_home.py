import logging
import tkinter
from functools import partial

import customtkinter
from PIL import Image

from src.gui.frames.safe_disposable_frame import SafeDisposableFrame

BTN_SIZE = (225, 86)
HOME_IM_SIZE = (441, 215)


class PageHome(SafeDisposableFrame):
    def __init__(self, master, root_callback: callable, **kwargs):
        super().__init__(master, **kwargs)
        logging.info("Create PageHome")

        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.canvas_width = 320
        self.canvas_height = 240

        # Top text
        top_label = customtkinter.CTkLabel(
            master=self, text="Grimassist Gesture Settings"
        )
        top_label.cget("font").configure(size=24)
        top_label.grid(row=0, column=0, padx=20, pady=20, sticky="new", columnspan=2)

        # Description
        des_txt = "Grimassist helps gamers control their mouse cursor using their head movement and facial gestures."
        des_label = customtkinter.CTkLabel(
            master=self, text=des_txt, wraplength=400, justify=tkinter.CENTER
        )
        des_label.cget("font").configure(size=14)
        des_label.grid(
            row=1, column=0, padx=20, pady=(5, 5), sticky="new", columnspan=2
        )

        # Disclaimer
        disc_txt = "Disclaimer: Grimassist is not intended for medical use."
        disc_label = customtkinter.CTkLabel(
            master=self,
            text=disc_txt,
            wraplength=700,
            text_color="gray60",
            justify=tkinter.CENTER,
        )
        disc_label.cget("font").configure(size=14)
        disc_label.grid(
            row=2, column=0, padx=20, pady=(5, 10), sticky="new", columnspan=2
        )

        # Page camera btn
        page_camera_btn_im = customtkinter.CTkImage(
            Image.open("assets/images/page_camera_btn.png"), size=BTN_SIZE
        )
        page_camera_btn = customtkinter.CTkButton(
            master=self,
            text="",
            border_width=0,
            corner_radius=12,
            image=page_camera_btn_im,
            command=partial(
                root_callback,
                function_name="change_page",
                args={"target": "page_camera"},
            ),
        )
        page_camera_btn.grid(row=3, column=0, padx=80, pady=10, sticky="nw")

        # Page cursor btn
        page_cursor_btn_im = customtkinter.CTkImage(
            Image.open("assets/images/page_cursor_btn.png"), size=BTN_SIZE
        )
        page_cursor_btn = customtkinter.CTkButton(
            master=self,
            text="",
            border_width=0,
            corner_radius=12,
            image=page_cursor_btn_im,
            command=partial(
                root_callback,
                function_name="change_page",
                args={"target": "page_cursor"},
            ),
        )
        page_cursor_btn.grid(row=4, column=0, padx=80, pady=10, sticky="nw")

        # Page gestures btn
        page_gestures_btn_im = customtkinter.CTkImage(
            Image.open("assets/images/page_gestures_btn.png"), size=BTN_SIZE
        )
        page_gestures_btn = customtkinter.CTkButton(
            master=self,
            text="",
            border_width=0,
            corner_radius=12,
            image=page_gestures_btn_im,
            command=partial(
                root_callback,
                function_name="change_page",
                args={"target": "page_gestures"},
            ),
        )
        page_gestures_btn.grid(row=5, column=0, padx=80, pady=10, sticky="nw")

        # Page keyboard btn
        page_keyboard_btn_im = customtkinter.CTkImage(
            Image.open("assets/images/page_keyboard_btn.png"), size=BTN_SIZE
        )
        page_keyboard_btn = customtkinter.CTkButton(
            master=self,
            text="",
            border_width=0,
            corner_radius=12,
            image=page_keyboard_btn_im,
            command=partial(
                root_callback,
                function_name="change_page",
                args={"target": "page_keyboard"},
            ),
        )
        page_keyboard_btn.grid(row=6, column=0, padx=80, pady=10, sticky="nw")

        # home image
        home_im = customtkinter.CTkImage(
            Image.open("assets/images/home_im.png"), size=HOME_IM_SIZE
        )
        label = customtkinter.CTkLabel(
            self, image=home_im, width=HOME_IM_SIZE[0], height=HOME_IM_SIZE[1], text=""
        )
        label.grid(row=3, column=1, padx=20, pady=20, rowspan=3, sticky="we")
