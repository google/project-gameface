import logging
import customtkinter

from src.gui import frames
from src.config_manager import ConfigManager
from src.controllers import Keybinder, MouseController
from src.gui.pages import (
    PageSelectCamera,
    PageCursor,
    PageSelectGestures,
    PageKeyboard,
    PageAbout,
)

customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme("assets/themes/google_theme.json")

logger = logging.getLogger("MainGUi")


class MainGui:
    def __init__(self, tk_root):
        logger.info("Init MainGui")
        super().__init__()
        self.tk_root = tk_root

        self.tk_root.geometry("1024x800")
        self.tk_root.title(f"Grimassist {ConfigManager().version}")
        self.tk_root.iconbitmap("assets/images/icon.ico")
        self.tk_root.resizable(width=True, height=True)

        self.tk_root.grid_rowconfigure(1, weight=1)
        self.tk_root.grid_columnconfigure(1, weight=1)

        # Create menu frame and assign callbacks
        self.frame_menu = frames.FrameMenu(
            self.tk_root,
            self.root_function_callback,
            height=360,
            width=260,
            logger_name="frame_menu",
        )
        self.frame_menu.grid(
            row=0, column=0, padx=0, pady=0, sticky="nsew", columnspan=1, rowspan=3
        )

        # Create Preview frame
        self.frame_preview = frames.FrameCamPreview(
            self.tk_root, self.cam_preview_callback, logger_name="frame_preview"
        )
        self.frame_preview.grid(
            row=1, column=0, padx=0, pady=0, sticky="sew", columnspan=1
        )
        self.frame_preview.enter()

        # Create all wizard pages and grid them.
        self.pages = [
            PageSelectCamera(
                master=self.tk_root,
            ),
            PageCursor(
                master=self.tk_root,
            ),
            PageSelectGestures(
                master=self.tk_root,
            ),
            PageKeyboard(
                master=self.tk_root,
            ),
            PageAbout(
                master=self.tk_root,
            ),
        ]

        self.current_page_name = None
        for page in self.pages:
            page.grid(
                row=0, column=1, padx=5, pady=5, sticky="nsew", rowspan=2, columnspan=1
            )

        self.change_page(PageSelectCamera.__name__)

        # Profile UI
        self.frame_profile_switcher = frames.FrameProfileSwitcher(
            self.tk_root, main_gui_callback=self.root_function_callback
        )
        self.frame_profile_editor = frames.FrameProfileEditor(
            self.tk_root, main_gui_callback=self.root_function_callback
        )

    def root_function_callback(self, function_name, args: dict = {}, **kwargs):
        logger.info(f"root_function_callback {function_name} with {args}")

        # Basic page navigate
        if function_name == "change_page":
            self.change_page(args["target"])
            self.frame_menu.set_tab_active(tab_name=args["target"])

        # Profiles
        elif function_name == "show_profile_switcher":
            self.frame_profile_switcher.enter()
        elif function_name == "show_profile_editor":
            self.frame_profile_editor.enter()

        elif function_name == "refresh_profiles":
            logger.info("refresh_profile")
            for page in self.pages:
                page.refresh_profile()

    def cam_preview_callback(self, function_name, args: dict, **kwargs):
        logger.info(f"cam_preview_callback {function_name} with {args}")

        if function_name == "toggle_switch":
            self.set_mediapipe_mouse_enable(new_state=args["switch_status"])

    def set_mediapipe_mouse_enable(self, new_state: bool):
        if new_state:
            Keybinder().set_active(True)
            MouseController().set_active(True)
        else:
            Keybinder().set_active(False)
            MouseController().set_active(False)

    def change_page(self, target_page_name: str):
        if self.current_page_name == target_page_name:
            return

        for page in self.pages:
            if page.__class__.__name__ == target_page_name:
                page.grid()
                page.enter()
                self.current_page_name = page.__class__.__name__

            else:
                page.grid_remove()
                page.leave()

    def del_main_gui(self):
        logger.info("Deleting MainGui instance")
        # try:
        self.frame_preview.leave()
        self.frame_preview.destroy()
        self.frame_menu.leave()
        self.frame_menu.destroy()
        for page in self.pages:
            page.leave()
            page.destroy()

        self.tk_root.quit()
        self.tk_root.destroy()
