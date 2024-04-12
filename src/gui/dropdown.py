from functools import partial

import customtkinter
from PIL import Image

from src.config_manager import ConfigManager

ITEM_HEIGHT = 48
ICON_SIZE = (68, 48)
MAX_ROWS = 10
Y_OFFSET = 30

LIGHT_BLUE = "#FBFBFF"


def mouse_in_widget(mouse_x, mouse_y, widget, expand_x=(0, 0), expand_y=(0, 0)):
    widget_x1 = widget.winfo_rootx() - expand_x[0]
    widget_y1 = widget.winfo_rooty() - expand_y[0]
    widget_x2 = widget_x1 + widget.winfo_width() + expand_x[0] + expand_x[1]
    widget_y2 = widget_y1 + widget.winfo_height() + expand_y[0] + expand_y[1]
    if (
        mouse_x >= widget_x1
        and mouse_x <= widget_x2
        and mouse_y >= widget_y1
        and mouse_y <= widget_y2
    ):
        return True
    else:
        return False


class Dropdown:
    def __init__(self, master, dropdown_items: dict, width, callback: callable):
        self.master_toplevel = master.winfo_toplevel()

        self.float_window = customtkinter.CTkToplevel(master)
        self.float_window.wm_overrideredirect(True)

        self.float_window.lift()
        self.float_window.wm_attributes("-topmost", True)
        # Hide icon in taskbar

        self.float_window.wm_attributes("-toolwindow", "True")
        self.float_window.grid_rowconfigure(MAX_ROWS, weight=1)
        self.float_window.grid_columnconfigure(1, weight=1)
        # self.float_window.group(master)
        self._displayed = True

        self.dropdown_keys = list(dropdown_items.keys())

        self.divs = self.create_divs(self.float_window, dropdown_items, width)
        self.button_names = [str(v["button"]) for k, v in self.divs.items()]
        self.selected_gesture = list(dropdown_items.keys())[0]

        self.bind_id_release = None
        self.bind_id_motion = None

        self.hide_dropdown()

        self.master_callback = callback

        self.current_user = None

    def create_divs(self, master, ges_images: dict, width: int) -> dict:
        divs = {}
        for row, (gesture, image_path) in enumerate(ges_images.items()):
            image = customtkinter.CTkImage(
                Image.open(image_path).resize(ICON_SIZE), size=ICON_SIZE
            )

            # Label ?
            row_btn = customtkinter.CTkButton(
                master=master,
                width=width,
                height=ITEM_HEIGHT,
                text=gesture,
                border_width=0,
                corner_radius=0,
                image=image,
                hover=True,
                fg_color=LIGHT_BLUE,
                hover_color="gray90",
                text_color_disabled="gray80",
                compound="left",
                anchor="nw",
            )

            row_btn.grid(row=row, column=0, padx=(0, 0), pady=(0, 0), sticky="nsew")

            divs[gesture] = {"button": row_btn, "image": image}

        return divs

    def mouse_release(self, event):
        """Release mouse and trigger button"""

        # Check if release which button
        for gesture, div in self.divs.items():
            button = div["button"]
            if button.cget("state") == "disabled":
                continue

            if mouse_in_widget(event.x_root, event.y_root, button):
                self.hide_dropdown()
                self.item_click_callback(gesture)

        return

    def mouse_motion(self, event):
        if not mouse_in_widget(
            event.x_root, event.y_root, self.float_window, expand_y=(Y_OFFSET, 0)
        ):
            self.hide_dropdown()
            return

        # Check if release which button
        for div in self.divs.values():
            button = div["button"]
            if button.cget("state") == "disabled":
                continue

            if mouse_in_widget(event.x_root, event.y_root, button):
                button.configure(fg_color="gray90")
            else:
                button.configure(fg_color=LIGHT_BLUE)

    def item_click_callback(self, target_gesture: str):
        self.selected_gesture = target_gesture
        self.hide_dropdown()
        self.master_callback(self.current_user, target_gesture)

        # Disable clicked option, except the first one
        if target_gesture != self.dropdown_keys[0]:
            self.disable_item(target_gesture)

    def disable_item(self, target_gesture):
        if target_gesture in self.divs:
            self.divs[target_gesture]["button"].configure(state="disabled")

    def enable_item(self, target_gesture):
        if target_gesture in self.divs:
            self.divs[target_gesture]["button"].configure(state="normal")

    def enable_all_except(self, target_gestures: list):
        for div_name in self.divs:
            if div_name in target_gestures:
                self.divs[div_name]["button"].configure(state="disabled")
            else:
                self.divs[div_name]["button"].configure(state="normal")

    def refresh_items(self):
        self.enable_all_except(
            list(ConfigManager().mouse_bindings.keys())
            + list(ConfigManager().keyboard_bindings.keys())
        )

    def register_widget(self, widget, name):
        widget.bind("<ButtonPress-1>", partial(self.show_dropdown, widget, name))

    def show_dropdown(self, widget, name, event):
        # Close the opening dropdown first
        if self._displayed:
            self.hide_dropdown()

        if not self._displayed:
            self.refresh_items()

            draw_x = widget.winfo_rootx()
            draw_y = widget.winfo_rooty() + Y_OFFSET

            self.float_window.wm_geometry(f"+{draw_x}+{draw_y}")
            self.float_window.deiconify()
            self.float_window.lift()

            # Use bind_all in case hold over label, canvas
            self.bind_id_release = self.float_window.bind_all(
                "<ButtonRelease-1>", self.mouse_release
            )
            self.bind_id_motion = self.float_window.bind_all(
                "<B1-Motion>", self.mouse_motion
            )
            self.float_window.wm_attributes("-disabled", False)

            # Set current user
            self.current_user = name
            self._displayed = True

    def hide_dropdown(self, event=None):
        if self._displayed:
            # Remove bindings and completely disable the window
            self.float_window.unbind("<ButtonRelease-1>", self.bind_id_release)
            self.float_window.unbind("<B1-Motion>", self.bind_id_motion)
            self.float_window.wm_attributes("-disabled", True)

            self._displayed = False

            # Reset color
            for div in self.divs.values():
                button = div["button"]
                button.configure(fg_color=LIGHT_BLUE)

            self.float_window.withdraw()
