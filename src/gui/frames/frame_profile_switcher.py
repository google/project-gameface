import logging
import time
import tkinter as tk
from functools import partial

import customtkinter
from PIL import Image

from src.config_manager import ConfigManager
from src.gui.frames.safe_disposable_frame import SafeDisposableFrame
from src.task_killer import TaskKiller

logger = logging.getLogger("FrameProfileSwitcher")

PROFILE_ITEM_SIZE = 231, 43
POPUP_OFFSET = 30, 5
MAX_PROF_ROWS = 11
PREFIX_ICON_SIZE = 36, 24
TOP_PAD = 6

EXTEND_PAD = 10

LIGHT_GREEN = "#a6eacf"
LIGHT_BLUE = "#e8f0fe"
MEDIUM_BLUE = "#D0E1F9"
DARK_BLUE = "#1A73E8"
BACKUP_PROFILE_NAME = "default"

DIV_COLORS = {"default": "white", "hovering": LIGHT_BLUE, "selected": MEDIUM_BLUE}


def random_name(row):
    return str(row) + str(hex(int(time.time() * 1000)))[2:]


class ItemProfileSwitcher(SafeDisposableFrame):
    def __init__(
        self,
        owner_frame,
        top_level,
        main_gui_callback,
        **kwargs,
    ):
        super().__init__(top_level, **kwargs)
        self.owner_frame = owner_frame
        self.main_gui_callback = main_gui_callback
        self.is_active = False

        self.grid_rowconfigure(MAX_PROF_ROWS, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.divs = self.load_initial_profiles()

        # self.set_div_selected(self.divs[div_id])

        # Custom border
        self.configure(border_color="gray60")
        self.configure(fg_color="transparent")
        self.configure(bg_color="transparent")
        self.configure(
            background_corner_colors=["#000000", "#000000", "#000000", "#000000"]
        )

    def load_initial_profiles(self):
        """Create div according to profiles in config"""
        profile_names = ConfigManager().list_profile()

        divs = {}
        row = 0
        for profile_name in profile_names:
            div_id = random_name(row)
            div = self.create_div(row, div_id, profile_name)
            div["wrap_label"].grid()

            # Random unique div id
            divs[div_id] = div
            row += 1

        # Create add profile button
        drop_add_div_id = random_name(row)
        addp_div = self.create_add_profiles_div(row, drop_add_div_id)
        addp_div["wrap_label"].grid()
        divs[drop_add_div_id] = addp_div
        row += 1

        # Create edit profile button
        edit_div_id = random_name(row)
        edit_div = self.create_edit_profiles_div(row, edit_div_id)
        edit_div["wrap_label"].grid()
        divs[edit_div_id] = edit_div

        return divs

    def get_div_id(self, profile_name: str):
        """Get div unique id from profile name"""
        for div_id, div in self.divs.items():
            if div["profile_name"] == profile_name:
                return div_id
        logger.critical(f"{profile_name} not found")
        TaskKiller().exit()

    def hover_enter(self, div, event):
        for widget_name, widget in div.items():
            target_widgets = ["wrap_label"]
            if widget is None:
                continue
            if widget_name in target_widgets:
                widget.configure(fg_color=DIV_COLORS["hovering"])
                # widget.configure(image=div["item_bg_hover"])

        div["is_hovering"] = True

    def hover_leave(self, div, event):
        for widget_name, widget in div.items():
            target_widgets = ["wrap_label"]
            if widget is None:
                continue
            if widget_name in target_widgets:
                widget.configure(fg_color="white")
                # widget.configure(image=div["item_bg"])

        div["is_hovering"] = False

    def remove_div(self, div_name):
        logger.info(f"Remove {div_name}")
        div = self.divs[div_name]

        for widget in div.values():
            if isinstance(
                widget, customtkinter.windows.widgets.core_widget_classes.CTkBaseClass
            ):
                widget.grid_forget()
                widget.destroy()

    def refresh_frame(self):
        """Refresh the divs if profile directory has changed"""

        logger.info("Refresh frame_profile")

        # Check if folders same as divs
        name_list = [div["profile_name"] for _, div in self.divs.items()]
        name_list.remove("Manage Profiles")
        name_list.remove("Add Profile")

        if set(ConfigManager().list_profile()) == set(name_list):
            return
        logger.info(
            f"Profile directory changed {ConfigManager().profiles} != {name_list}, reload..."
        )

        # Delete all divs and re-create
        self.clear_divs()
        self.divs = self.load_initial_profiles()
        current_profile = ConfigManager().current_profile_name.get()

        # Check if selected profile exist
        new_name_list = [div["profile_name"] for _, div in self.divs.items()]
        if current_profile not in new_name_list:
            logger.critical(f"Profile {current_profile} not found.")
            TaskKiller().exit()

        self.owner_frame.show_window()
        logger.info(f"Current selected profile {current_profile}")

    def clear_divs(self):
        for div_id, div in self.divs.items():
            self.remove_div(div_id)
        self.divs = {}

    def switch_div_profile(self, div, event):
        # profile item click callback
        ConfigManager().switch_profile(div["profile_name"])
        # Refresh values in each page
        self.main_gui_callback("refresh_profiles")
        self.owner_frame.hide_window()

    def create_div(self, row: int, div_id: str, profile_name) -> dict:
        prefix_icon = customtkinter.CTkImage(
            Image.open("assets/images/proj_icon_blank.png"), size=PREFIX_ICON_SIZE
        )

        # Box
        entry_var = tk.StringVar()
        entry_var.set(profile_name)
        wrap_label = customtkinter.CTkLabel(
            self,
            text="",
            textvariable=entry_var,
            height=40,
            image=prefix_icon,
            compound="left",
            anchor="w",
            cursor="hand2",
            fg_color="white",
            corner_radius=0,
        )

        top_pad = TOP_PAD if row == 0 else 0
        wrap_label.grid(
            row=row,
            column=0,
            padx=(1, 2),
            pady=(top_pad, 0),
            ipadx=0,
            ipady=0,
            sticky="new",
        )

        sep = tk.ttk.Separator(wrap_label, orient="horizontal")
        sep.grid(row=row, column=0, padx=0, pady=0, ipadx=0, ipady=0, sticky="sew")

        div = {
            "div_id": div_id,
            "profile_name": profile_name,
            "wrap_label": wrap_label,
            "entry_var": entry_var,
            "is_hovering": False,
        }

        # Hover effect
        for widget in [wrap_label]:
            if widget is None:
                continue
            widget.bind("<Enter>", partial(self.hover_enter, div))
            widget.bind("<Leave>", partial(self.hover_leave, div))

        # Click label : swap profile function
        for widget in [wrap_label]:
            widget.bind("<Button-1>", partial(self.switch_div_profile, div))

        return div

    def create_edit_profiles_div(self, row: int, div_id: str) -> dict:
        prefix_icon = customtkinter.CTkImage(
            Image.open("assets/images/edit.png"), size=PREFIX_ICON_SIZE
        )

        # Box
        wrap_label = customtkinter.CTkLabel(
            self,
            text="Manage Profiles",
            height=40,
            image=prefix_icon,
            compound="left",
            justify="left",
            anchor="w",
            cursor="hand2",
            fg_color="white",
            corner_radius=0,
        )

        top_pad = TOP_PAD if row == 0 else 0
        wrap_label.grid(
            row=row,
            column=0,
            padx=(1, 2),
            pady=(top_pad, 0),
            ipadx=0,
            ipady=0,
            sticky="new",
        )

        div = {
            "div_id": div_id,
            "profile_name": "Manage Profiles",
            "wrap_label": wrap_label,
            "is_hovering": False,
        }

        # Hover effect
        for widget in [wrap_label]:
            if widget is None:
                continue
            widget.bind("<Enter>", partial(self.hover_enter, div))
            widget.bind("<Leave>", partial(self.hover_leave, div))

        # Click label : swap profile function
        for widget in [wrap_label]:
            widget.bind("<Button-1>", self.owner_frame.show_profile_editor)

        return div

    def create_add_profiles_div(self, row: int, div_id: str) -> dict:
        prefix_icon = customtkinter.CTkImage(
            Image.open("assets/images/add_drop.png"), size=PREFIX_ICON_SIZE
        )

        # Box
        wrap_label = customtkinter.CTkLabel(
            self,
            text="Add Profile",
            height=40,
            image=prefix_icon,
            compound="left",
            justify="left",
            anchor="w",
            cursor="hand2",
            fg_color="white",
            corner_radius=0,
        )

        top_pad = TOP_PAD if row == 0 else 0
        wrap_label.grid(
            row=row,
            column=0,
            padx=(1, 2),
            pady=(top_pad, 0),
            ipadx=0,
            ipady=0,
            sticky="new",
        )

        div = {
            "div_id": div_id,
            "profile_name": "Add Profile",
            "wrap_label": wrap_label,
            "is_hovering": False,
        }

        # Hover effect
        for widget in [wrap_label]:
            if widget is None:
                continue
            widget.bind("<Enter>", partial(self.hover_enter, div))
            widget.bind("<Leave>", partial(self.hover_leave, div))

        # Click label : swap profile function
        for widget in [wrap_label]:
            widget.bind("<Button-1>", self.owner_frame.dropdown_add_profile)

        return div

    def enter(self):
        super().enter()
        self.refresh_frame()

    def leave(self):
        super().leave()


class FrameProfileSwitcher:
    def __init__(self, root_window, main_gui_callback: callable, **kwargs):
        self.root_window = root_window
        self.main_gui_callback = main_gui_callback
        self.float_window = customtkinter.CTkToplevel(root_window)
        self.float_window.wm_overrideredirect(True)
        self.float_window.lift()
        self.float_window.wm_attributes("-disabled", True)
        self.float_window.wm_attributes("-toolwindow", "True")
        self.float_window.grid_rowconfigure(3, weight=1)
        self.float_window.grid_columnconfigure(0, weight=1)
        self.float_window.configure(fg_color="white")
        self._displayed = True
        # Rounded corner
        self.float_window.config(background="#000000")
        self.float_window.attributes("-transparentcolor", "#000000")

        # Custom border
        self.float_window.configure(highlightthickness=0, bd=0)

        n_rows = len(ConfigManager().list_profile()) + 2
        self.float_window.geometry(
            f"{PROFILE_ITEM_SIZE[0]}x{PROFILE_ITEM_SIZE[1]*n_rows+EXTEND_PAD}+{POPUP_OFFSET[0]}+{POPUP_OFFSET[1]}"
        )

        # Inner frame
        self.inner_frame = ItemProfileSwitcher(
            owner_frame=self,
            top_level=self.float_window,
            main_gui_callback=main_gui_callback,
        )
        self.inner_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nswe")

        self.hide_window()
        self.root_window.bind("<Configure>", self.hide_window)

        self.prev_event = None

    def change_profile(self, target):
        ConfigManager().switch_profile(target)
        self.pages["page_camera"].refresh_profile()
        self.pages["page_cursor"].refresh_profile()
        self.pages["page_gestures"].refresh_profile()
        self.pages["page_keyboard"].refresh_profile()

    def show_window(self):
        self.root_window.bind("<Configure>", self.hide_window)
        shift_x = self.root_window.winfo_rootx()
        shift_y = self.root_window.winfo_rooty()

        # Popup
        n_rows = len(ConfigManager().profiles) + 2

        self.float_window.geometry(
            f"{PROFILE_ITEM_SIZE[0]}x{PROFILE_ITEM_SIZE[1]*n_rows+EXTEND_PAD}+{POPUP_OFFSET[0]+shift_x}+{POPUP_OFFSET[1]+shift_y}"
        )

        self.float_window.deiconify()
        self.float_window.lift()
        self.float_window.wm_attributes("-disabled", False)
        self._displayed = True

    def hide_window(self, event=None):
        if self._displayed:
            logger.info("hide")
            self.root_window.unbind_all("<Configure>")

            self.float_window.wm_attributes("-disabled", True)
            self._displayed = False

            self.float_window.withdraw()

    def show_profile_editor(self, event, **kwargs):
        self.hide_window()
        self.main_gui_callback("show_profile_editor")

    def dropdown_add_profile(self, event, **kwargs):
        ConfigManager().add_profile()
        self.inner_frame.refresh_frame()
        self.show_window()

    def enter(self):
        # refresh UI
        self.inner_frame.enter()
        self.show_window()
        logger.info("enter")

    def leave(self):
        super().leave()
        self.inner_frame.leave()
        logger.info("leave")
