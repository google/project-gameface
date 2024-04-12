import time
import logging
import tkinter as tk
import re
from functools import partial

import customtkinter
from PIL import Image

from src.config_manager import ConfigManager
from src.task_killer import TaskKiller
from src.gui.frames.safe_disposable_frame import SafeDisposableFrame
from src.gui.frames.safe_disposable_scrollable_frame import (
    SafeDisposableScrollableFrame,
)


logger = logging.getLogger("FrameProfile")

CLOSE_ICON_SIZE = 24, 24
POPUP_SIZE = 350, 600
POPUP_OFFSET = 337, 30
MAX_PROF_ROWS = 11
EDIT_ICON_SIZE = (24, 24)
BIN_ICON_SIZE = (24, 24)

LIGHT_GREEN = "#a6eacf"
LIGHT_BLUE = "#e8f0fe"
MEDIUM_BLUE = "#D0E1F9"
DARK_BLUE = "#1A73E8"
BACKUP_PROFILE_NAME = "default"

DIV_COLORS = {"default": "white", "hovering": LIGHT_BLUE, "selected": MEDIUM_BLUE}


class FrameProfileItems(SafeDisposableScrollableFrame):
    def __init__(
        self,
        master,
        refresh_master_fn,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.refresh_master_fn = refresh_master_fn
        self.is_active = False

        self.grid_rowconfigure(MAX_PROF_ROWS, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.edit_image = customtkinter.CTkImage(
            Image.open("assets/images/edit.png").resize(EDIT_ICON_SIZE),
            size=EDIT_ICON_SIZE,
        )

        self.bin_image = customtkinter.CTkImage(
            Image.open("assets/images/bin.png").resize(BIN_ICON_SIZE),
            size=BIN_ICON_SIZE,
        )

        self.divs = self.load_initial_profiles()

        div_id = self.get_div_id(ConfigManager().current_profile_name.get())
        self.set_div_selected(self.divs[div_id])

    def load_initial_profiles(self):
        """Create div according to profiles in config"""
        profile_names = ConfigManager().list_profile()

        divs = {}
        for row, profile_name in enumerate(profile_names):
            div_id = str(row) + str(hex(int(time.time() * 1000)))[2:]
            div = self.create_div(row, div_id, profile_name)
            div["wrap_label"].grid()

            # Random unique div id
            divs[div_id] = div

        return divs

    def hover_enter(self, div, event):
        if div["is_selected"]:
            return
        for widget_name, widget in div.items():
            target_widgets = ["wrap_label", "entry", "edit_button", "bin_button"]
            if widget is None:
                continue
            if div["is_editing"]:
                target_widgets.remove("entry")
            if widget_name in target_widgets:
                widget.configure(fg_color=DIV_COLORS["hovering"])

        div["is_hovering"] = True

    def hover_leave(self, div, event):
        if div["is_selected"]:
            return
        for widget_name, widget in div.items():
            target_widgets = ["wrap_label", "entry", "edit_button", "bin_button"]
            if widget is None:
                continue
            if div["is_editing"]:
                target_widgets.remove("entry")
            if widget_name in target_widgets:
                widget.configure(fg_color="white")
        div["is_hovering"] = False

    def get_div_id(self, profile_name: str):
        """Get div unique id from profile name"""
        for div_id, div in self.divs.items():
            if div["profile_name"] == profile_name:
                return div_id
        logger.critical(f"{profile_name} not found")
        TaskKiller().exit()

    def set_div_inactive(self, target_div):
        for widget_name, widget in target_div.items():
            target_widgets = ["wrap_label", "entry", "edit_button", "bin_button"]
            if widget is None:
                continue

            if target_div["is_editing"]:
                target_widgets.remove("entry")

            if widget_name in target_widgets:
                widget.configure(fg_color="white")

        target_div["is_selected"] = False

    def set_div_selected(self, div: dict, event=None):
        logger.info(f"set selected to {div['profile_name']}")

        if div["is_selected"]:
            return

        for div_id, d in self.divs.items():
            self.set_div_inactive(d)
            d["is_selected"] = False

        for widget_name, widget in div.items():
            target_widgets = ["wrap_label", "entry", "edit_button", "bin_button"]
            if widget is None:
                continue

            if div["is_editing"]:
                target_widgets.remove("entry")
            if widget_name in target_widgets:
                widget.configure(fg_color=DIV_COLORS["selected"])

        div["is_selected"] = True
        ConfigManager().switch_profile(div["profile_name"])

        # Refresh values in each page
        self.refresh_master_fn()

    def remove_div(self, div_name):
        logger.info(f"Remove {div_name}")
        div = self.divs[div_name]

        for widget in div.values():
            if isinstance(
                widget, customtkinter.windows.widgets.core_widget_classes.CTkBaseClass
            ):
                widget.grid_forget()
                widget.destroy()
        self.refresh_scrollbar()

    def clear_divs(self):
        for div_id, div in self.divs.items():
            self.remove_div(div_id)
        self.divs = {}

    def refresh_frame(self):
        """Refresh the divs if profile directory has changed"""

        logger.info("Refresh frame_profile")

        # Check if folders same as divs
        name_list = [div["profile_name"] for _, div in self.divs.items()]
        if ConfigManager().list_profile() == name_list:
            return
        logger.info("Profile directory changed, reload...")

        # Delete all divs and re-create
        self.clear_divs()
        self.divs = self.load_initial_profiles()
        current_profile = ConfigManager().current_profile_name.get()

        # Check if selected profile exist
        new_name_list = [div["profile_name"] for _, div in self.divs.items()]
        if current_profile not in new_name_list:
            logger.critical(f"Profile {current_profile} not found.")
            TaskKiller().exit()

        # Set and highlight selected profile
        for div_id, div in self.divs.items():
            if div["profile_name"] == current_profile:
                self.set_div_selected(div)
            else:
                self.set_div_inactive(div)
        self.refresh_scrollbar()
        logger.info(f"Current selected profile {current_profile}")

    def rename_button_callback(self, div: dict):
        # Hide all rename buttons
        for _, hdiv in self.divs.items():
            if hdiv["edit_button"] is None:
                continue
            hdiv["edit_button"].grid_remove()

        div["is_editing"] = True
        div["entry"].configure(
            state="normal", border_width=2, border_color=LIGHT_GREEN, fg_color="white"
        )
        div["entry"].focus_set()
        div["entry"].icursor("end")

    def check_profile_name_valid(self, div, var, index, mode):
        pattern = re.compile(r"^[a-zA-Z0-9_-]+$")
        is_valid_input = bool(pattern.match(div["entry_var"].get()))

        # Change border color
        if is_valid_input:
            div["entry"].configure(border_width=2, border_color=LIGHT_GREEN)
        else:
            div["entry"].configure(border_width=2, border_color="#ee9e9d")

        return is_valid_input

    def finish_rename(self, div, event):
        if not self.check_profile_name_valid(div, None, None, None):
            logger.warning("Invalid profile name")
            return

        div["is_editing"] = False

        if div["is_selected"]:
            new_color = DIV_COLORS["selected"]
        elif div["is_hovering"]:
            new_color = DIV_COLORS["hovering"]
        else:
            new_color = DIV_COLORS["default"]

        div["entry"].configure(state="disabled", fg_color=new_color, border_width=0)
        ConfigManager().rename_profile(div["profile_name"], div["entry_var"].get())
        ConfigManager().switch_profile(div["entry_var"].get())
        div["profile_name"] = div["entry_var"].get()

        # Show all rename buttons
        for div_id, div in self.divs.items():
            if div["edit_button"] is None:
                continue
            div["edit_button"].grid()

    def remove_button_callback(self, div):
        ConfigManager().remove_profile(div["profile_name"])
        if div["profile_name"] == ConfigManager().current_profile_name.get():
            default_div_id = self.get_div_id(BACKUP_PROFILE_NAME)
            self.set_div_selected(self.divs[default_div_id])

        self.refresh_frame()

    def create_div(self, row: int, div_id: str, profile_name) -> dict:
        # Box wrapper
        wrap_label = customtkinter.CTkLabel(
            self, text="", height=54, fg_color="white", corner_radius=10
        )
        wrap_label.grid(row=row, column=0, padx=10, pady=4, sticky="new")

        # Edit button
        if profile_name != BACKUP_PROFILE_NAME:
            edit_button = customtkinter.CTkButton(
                self,
                text="",
                width=20,
                border_width=0,
                corner_radius=0,
                image=self.edit_image,
                hover=False,
                compound="right",
                fg_color="transparent",
                anchor="e",
                command=None,
            )

            edit_button.grid(
                row=row,
                column=0,
                padx=(0, 55),
                pady=(20, 0),
                sticky="ne",
                columnspan=10,
                rowspan=10,
            )
        else:
            edit_button = None

        # Bin button
        if profile_name != BACKUP_PROFILE_NAME:
            bin_button = customtkinter.CTkButton(
                self,
                text="",
                width=20,
                border_width=0,
                corner_radius=0,
                image=self.bin_image,
                hover=False,
                compound="right",
                fg_color="transparent",
                anchor="e",
                command=None,
            )

            bin_button.grid(
                row=row,
                column=0,
                padx=(0, 20),
                pady=(20, 0),
                sticky="ne",
                columnspan=10,
                rowspan=10,
            )
        else:
            bin_button = None

        # Entry
        entry_var = tk.StringVar()
        entry_var.set(profile_name)
        entry = customtkinter.CTkEntry(
            self,
            textvariable=entry_var,
            placeholder_text="",
            width=170,
            height=30,
            corner_radius=0,
            state="disabled",
            border_width=0,
            insertborderwidth=0,
            fg_color="white",
        )
        entry.cget("font").configure(size=16)
        entry.grid(row=row, column=0, padx=20, pady=20, ipadx=10, ipady=0, sticky="nw")

        div = {
            "div_id": div_id,
            "profile_name": profile_name,
            "wrap_label": wrap_label,
            "entry": entry,
            "entry_var": entry_var,
            "edit_button": edit_button,
            "bin_button": bin_button,
            "is_hovering": False,
            "is_editing": False,
            "is_selected": False,
        }

        # Hover effect
        for widget in [wrap_label, entry, edit_button, bin_button]:
            if widget is None:
                continue
            widget.bind("<Enter>", partial(self.hover_enter, div))
            widget.bind("<Leave>", partial(self.hover_leave, div))

        # Click label : swap profile function
        for widget in [wrap_label, entry]:
            widget.bind("<Button-1>", partial(self.set_div_selected, div))

        # Bin button :  remove div function
        if bin_button is not None:
            bin_button.configure(command=partial(self.remove_button_callback, div))

        # Edit button : rename profile function
        if edit_button is not None:
            edit_button.configure(command=partial(self.rename_button_callback, div))
        entry_var.trace("w", partial(self.check_profile_name_valid, div))
        entry.bind("<Return>", command=partial(self.finish_rename, div))

        return div

    def enter(self):
        super().enter()
        self.refresh_frame()
        self.refresh_scrollbar()

    def leave(self):
        super().leave()


class FrameProfile(SafeDisposableFrame):
    def __init__(self, master, refresh_master_fn: callable, **kwargs):
        super().__init__(master, **kwargs)
        self.master_window = master
        self.float_window = customtkinter.CTkToplevel(master)
        self.float_window.wm_overrideredirect(True)
        self.float_window.lift()
        self.float_window.wm_attributes("-disabled", True)
        self.float_window.wm_attributes("-toolwindow", "True")
        self.float_window.grid_rowconfigure(3, weight=1)
        self.float_window.grid_columnconfigure(0, weight=1)
        self.float_window.configure(fg_color="white")
        # self.float_window.attributes('-topmost', True)
        self.float_window.geometry(
            f"{POPUP_SIZE[0]}x{POPUP_SIZE[1]}+{POPUP_OFFSET[0]}+{POPUP_OFFSET[1]}"
        )

        # Gray overlay
        self.shadow_window = customtkinter.CTkToplevel(master)
        self.shadow_window.configure(fg_color="black")
        self.shadow_window.wm_attributes("-alpha", 0.7)
        self.shadow_window.wm_overrideredirect(True)
        self.shadow_window.lift()
        self.shadow_window.wm_attributes("-toolwindow", "True")
        # self.shadow_window.attributes('-topmost', True)
        self.shadow_window.geometry(
            f"{self.master_window.winfo_width()}x{self.master_window.winfo_height()}"
        )

        # Label
        top_label = customtkinter.CTkLabel(
            master=self.float_window, text="User profiles"
        )
        top_label.cget("font").configure(size=24)
        top_label.grid(row=0, column=0, padx=20, pady=20, sticky="nw", columnspan=1)

        # Description label
        des_label = customtkinter.CTkLabel(
            master=self.float_window,
            text="With profile manager you can create and manage multiple profiles for each usage, so that you can easily switch between them.",
            wraplength=300,
            justify=tk.LEFT,
        )
        des_label.cget("font").configure(size=14)
        des_label.grid(row=1, column=0, padx=20, pady=10, sticky="nw")

        # Close button
        self.close_icon = customtkinter.CTkImage(
            Image.open("assets/images/close.png").resize(CLOSE_ICON_SIZE),
            size=CLOSE_ICON_SIZE,
        )

        close_btn = customtkinter.CTkButton(
            master=self.float_window,
            text="",
            image=self.close_icon,
            fg_color="white",
            hover_color="white",
            border_width=0,
            corner_radius=4,
            width=24,
            command=self.hide_window,
        )
        close_btn.grid(
            row=0, column=0, padx=10, pady=10, sticky="ne", columnspan=1, rowspan=1
        )

        # Add  button
        add_button = customtkinter.CTkButton(
            master=self.float_window,
            text="+ Add profile",
            fg_color="white",
            width=100,
            text_color=DARK_BLUE,
            command=self.add_button_callback,
        )
        add_button.grid(row=2, column=0, padx=15, pady=5, sticky="nw")

        # Inner scrollable frame
        self.inner_frame = FrameProfileItems(self.float_window, refresh_master_fn)
        self.inner_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nswe")

        self._displayed = True
        self.hide_window()

        # Make new windows stick with root window
        self.master_window.bind("<Configure>", self.follow_window)
        self.master_window.bind("<FocusIn>", self.lift_window)

        self.prev_event = None

    def add_button_callback(self):
        ConfigManager().add_profile()
        self.inner_frame.refresh_frame()

    def lift_window(self, event):
        """Lift windows when root window get focus"""
        self.shadow_window.lift()
        self.float_window.lift()

    def follow_window(self, event):
        """Move profile window when root window is moved"""
        if self.prev_event is None:
            self.prev_event = event

        # Clicked but not moved
        if (self.prev_event.x == event.x) and (self.prev_event.y == event.y):
            self.lift_window(None)
            self.prev_event = event
            return

        shift_x = self.master_window.winfo_rootx()
        shift_y = self.master_window.winfo_rooty()
        self.float_window.geometry(
            f"+{POPUP_OFFSET[0]+shift_x}+{POPUP_OFFSET[1]+shift_y}"
        )
        self.shadow_window.geometry(f"+{shift_x}+{shift_y}")
        self.prev_event = event

    def change_profile(self, target):
        ConfigManager().switch_profile(target)
        self.pages["page_camera"].refresh_profile()
        self.pages["page_cursor"].refresh_profile()
        self.pages["page_gestures"].refresh_profile()
        self.pages["page_keyboard"].refresh_profile()

    def show_window(self):
        # Close the opening dropdown first
        if self._displayed:
            self.hide_window()

        if not self._displayed:
            logger.info("show")
            self.inner_frame.enter()

            shift_x = self.master_window.winfo_rootx()
            shift_y = self.master_window.winfo_rooty()

            # Gray overlay
            self.shadow_window.geometry(f"+{shift_x}+{shift_y}")
            self.shadow_window.deiconify()
            self.shadow_window.lift()
            self.shadow_window.wm_attributes("-disabled", True)

            # Popup
            self.float_window.geometry(
                f"+{POPUP_OFFSET[0]+shift_x}+{POPUP_OFFSET[1]+shift_y}"
            )
            self.float_window.deiconify()
            self.float_window.lift()
            self.float_window.wm_attributes("-disabled", False)
            self._displayed = True

    def hide_window(self, event=None):
        if self._displayed:
            logger.info("hide")
            self.float_window.wm_attributes("-disabled", True)
            self._displayed = False

            self.float_window.withdraw()
            self.shadow_window.withdraw()

    def enter(self):
        super().enter()
        self.inner_frame.enter()
        logger.info("enter")

    def leave(self):
        super().leave()
        self.inner_frame.leave()
        logger.info("leave")
