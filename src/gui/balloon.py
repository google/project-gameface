from functools import partial

import customtkinter
from PIL import Image

BALLOON_SIZE = (305, 80)


class Balloon:
    def __init__(self, master, image_path: str):
        self.float_window = customtkinter.CTkToplevel(master)
        self.float_window.wm_overrideredirect(True)
        self.float_window.lift()
        self.float_window.wm_attributes("-topmost", True)
        self.float_window.wm_attributes("-disabled", True)
        self.float_window.wm_attributes("-transparentcolor", "white")

        # Hide icon in taskbar
        self.float_window.wm_attributes("-toolwindow", "True")

        self.balloon_image = customtkinter.CTkImage(
            Image.open(image_path).resize(BALLOON_SIZE), size=BALLOON_SIZE
        )

        self.label = customtkinter.CTkLabel(
            self.float_window,
            text="",
            compound="center",
            # anchor="nw",
            justify="left",
            width=BALLOON_SIZE[0],
            height=BALLOON_SIZE[1],
            text_color="#3C4043",
            image=self.balloon_image,
        )
        self.label.cget("font").configure(size=16)

        self.label.grid(row=0, column=0, sticky="nsew")

        self._displayed = False
        self.float_window.withdraw()
        self.float_window.group(master)

    def register_widget(self, widget, text: str):
        if text != "":
            widget.bind("<Enter>", partial(self.show_balloon, widget, text))
            widget.bind("<Leave>", partial(self.hide_balloon, widget))

    def show_balloon(self, widget, text, event):
        if not self._displayed:
            self.label.configure(text=text)
            self._displayed = True
            self.float_window.wm_geometry(
                f"{BALLOON_SIZE[0]}x{BALLOON_SIZE[1]}+{widget.winfo_rootx()+widget.winfo_width()}+{widget.winfo_rooty()-10}"
            )

            self.float_window.lift()
            self.float_window.deiconify()

    def hide_balloon(self, widget, event):
        if self._displayed:
            self._displayed = False
            self.float_window.withdraw()
