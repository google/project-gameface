import tkinter

import customtkinter
from PIL import Image, ImageTk

from src.camera_manager import CameraManager
from src.config_manager import ConfigManager
from src.controllers import Keybinder
from src.gui.frames.safe_disposable_frame import SafeDisposableFrame

CANVAS_WIDTH = 216
CANVAS_HEIGHT = 162
LIGHT_BLUE = "#F9FBFE"
TOGGLE_ICON_SIZE = (32, 20)


class FrameCamPreview(SafeDisposableFrame):
    def __init__(self, master, master_callback: callable, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.configure(fg_color=LIGHT_BLUE)

        # Canvas.
        self.placeholder_im = Image.open("assets/images/placeholder.png")
        self.placeholder_im = ImageTk.PhotoImage(
            image=self.placeholder_im.resize((CANVAS_WIDTH, CANVAS_HEIGHT))
        )

        self.canvas = tkinter.Canvas(
            master=self,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg=LIGHT_BLUE,
            bd=0,
            relief="ridge",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, padx=10, pady=10, sticky="sw")

        # Toggle label
        self.toggle_label = customtkinter.CTkLabel(
            master=self,
            compound="right",
            text="Face control",
            text_color="black",
            justify=tkinter.LEFT,
        )
        self.toggle_label.cget("font").configure(size=14)
        self.toggle_label.grid(row=1, column=0, padx=(10, 0), pady=5, sticky="nw")

        # Toggle switch
        self.toggle_switch = customtkinter.CTkSwitch(
            master=self,
            text="",
            width=200,
            border_color="transparent",
            switch_height=18,
            switch_width=32,
            variable=Keybinder().is_active,
            command=lambda: master_callback(
                "toggle_switch", {"switch_status": self.toggle_switch.get()}
            ),
            onvalue=1,
            offvalue=0,
        )
        if ConfigManager().config["auto_play"]:
            self.toggle_switch.select()

        self.toggle_switch.grid(row=1, column=0, padx=(100, 0), pady=5, sticky="nw")

        # Toggle description label
        self.toggle_label = customtkinter.CTkLabel(
            master=self,
            compound="right",
            text="Allow facial gestures to control\nyour actions. ",
            text_color="#444746",
            justify=tkinter.LEFT,
        )
        self.toggle_label.cget("font").configure(size=12)
        self.toggle_label.grid(row=2, column=0, padx=(10, 0), pady=5, sticky="nw")

        # Set first image.
        self.canvas_image = self.canvas.create_image(
            0, 0, image=self.placeholder_im, anchor=tkinter.NW
        )
        self.new_photo = None
        self.after(1, self.camera_loop)

    def camera_loop(self):
        if self.is_destroyed:
            return
        if self.is_active:
            if CameraManager().is_destroyed:
                return
            frame_rgb = CameraManager().get_debug_frame()
            # Assign ref to avoid garbage collected
            self.new_photo = ImageTk.PhotoImage(
                image=Image.fromarray(frame_rgb).resize((CANVAS_WIDTH, CANVAS_HEIGHT))
            )
            self.canvas.itemconfig(self.canvas_image, image=self.new_photo)
            self.canvas.update()

            self.after(ConfigManager().config["tick_interval_ms"], self.camera_loop)

    def enter(self):
        super().enter()
        self.after(1, self.camera_loop)

    def destroy(self):
        super().destroy()
