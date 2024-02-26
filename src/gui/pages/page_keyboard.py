import logging
import tkinter as tk
import uuid
from functools import partial

import customtkinter
from PIL import Image

import src.shape_list as shape_list
from src.config_manager import ConfigManager
from src.detectors import FaceMesh
from src.gui.balloon import Balloon
from src.gui.dropdown import Dropdown
from src.gui.frames.safe_disposable_frame import SafeDisposableFrame
from src.gui.frames.safe_disposable_scrollable_frame import SafeDisposableScrollableFrame
from src.utils.Trigger import Trigger

logger = logging.getLogger("PageKeyboard")

DEFAULT_TRIGGER_TYPE = "hold"
LIGHT_RED = "#F95245"
RED = "#E94235"
GREEN = "#34A853"
YELLOW = "#FABB05"
LIGHT_BLUE = "#FBFBFF"
BLUE = "#1A73E8"
PAD_X = 40
DIV_WIDTH = 240
HELP_ICON_SIZE = (18, 18)
A_BUTTON_SIZE = (96, 48)
BIN_ICON_SIZE = (24, 24)

BALLOON_TXT = "Set how prominent your gesture has\nto be in order to trigger the action"


class FrameSelectKeyboard(SafeDisposableScrollableFrame):

    def __init__(
        self,
        master,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.is_active = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Float UIs
        self.shared_info_balloon = Balloon(
            self, image_path="assets/images/balloon.png")
        self.shared_dropdown = Dropdown(
            self,
            dropdown_items=shape_list.available_gestures,
            width=DIV_WIDTH,
            callback=self.dropdown_callback)

        self.help_icon = customtkinter.CTkImage(
            Image.open("assets/images/help.png").resize(HELP_ICON_SIZE),
            size=HELP_ICON_SIZE)

        self.a_button_image = customtkinter.CTkImage(
            Image.open("assets/images/a_button.png").resize(A_BUTTON_SIZE),
            size=A_BUTTON_SIZE)

        self.blank_a_button_image = customtkinter.CTkImage(Image.open(
            "assets/images/blank_a_button.png").resize(A_BUTTON_SIZE),
                                                           size=A_BUTTON_SIZE)

        self.a_button_active_image = customtkinter.CTkImage(Image.open(
            "assets/images/a_button_active.png").resize(A_BUTTON_SIZE),
                                                            size=A_BUTTON_SIZE)

        self.bin_image = customtkinter.CTkImage(
            Image.open("assets/images/bin.png").resize(BIN_ICON_SIZE),
            size=BIN_ICON_SIZE)

        self.wait_for_key_bind_id = None
        self.next_empty_row = 0
        self.waiting_div = None
        self.waiting_button = None
        self.slider_dragging = False

        # Divs
        self.divs = {}
        self.load_initial_keybindings()

    def load_initial_keybindings(self):
        """Load default from config and set the UI
        """
        for gesture_name, bind_info in ConfigManager().keyboard_bindings.items(
        ):
            div_name = f"div_{self.next_empty_row}"

            div = self.create_div(self.next_empty_row, div_name, gesture_name,
                                  bind_info)

            # Show elements related to gesture
            div["selected_gesture"] = gesture_name
            div["entry_field"].configure(image=self.blank_a_button_image)
            div["combobox"].set(gesture_name)
            div["slider"].set(int(bind_info[2] * 100))
            div["combobox"].grid()
            div["tips_label"].grid()
            div["subtle_label"].grid()
            div["slider"].grid()
            div["volume_bar"].grid()
            div["trigger_dropdown"].grid()
            self.shared_dropdown.disable_item(gesture_name)
            self.divs[div_name] = div
            self.next_empty_row += 1

        self.shared_dropdown.refresh_items()
        self.refresh_scrollbar()

    def add_blank_div(self):
        new_uuid = uuid.uuid1()
        div_name = f"div_{new_uuid}"
        logger.info(f"Add {div_name}")
        div = self.create_div(row=self.next_empty_row,
                              div_name=div_name,
                              gesture_name="None",
                              bind_info=["keyboard", "None", 0.5, "hold"])

        self.divs[div_name] = div
        self.next_empty_row += 1
        self.refresh_scrollbar()

    def remove_keybind(self, selected_key_action, selected_gesture):
        logger.info(f"Remove keyboard binding {selected_key_action}")
        ConfigManager().remove_temp_keyboard_binding(
            device="keyboard",
            key_action=selected_key_action,
            gesture=selected_gesture)
        ConfigManager().apply_keyboard_bindings()
        self.shared_dropdown.hide_dropdown()
        self.shared_dropdown.enable_item(selected_gesture)

    def bin_button_callback(self, div_name, event):
        div = self.divs[div_name]
        self.remove_div(div_name)
        self.remove_keybind(div["selected_key_action"], div["selected_gesture"])

        self.divs.pop(div_name)
        self.refresh_scrollbar()

    def remove_div(self, div_name):
        logger.info(f"Remove {div_name}")
        div = self.divs[div_name]

        for widget in div.values():
            if isinstance(
                    widget, customtkinter.windows.widgets.core_widget_classes.
                    CTkBaseClass):
                widget.grid_forget()
                widget.destroy()

    def create_div(self, row: int, div_name: str, gesture_name: str,
                   bind_info: list):
        _, key_action, thres, _ = bind_info

        # Bin button
        remove_button = customtkinter.CTkButton(master=self,
                                                text="",
                                                hover=False,
                                                image=self.bin_image,
                                                fg_color="white",
                                                anchor="e",
                                                cursor="hand2",
                                                width=25)

        remove_button.cget("font").configure(size=18)
        remove_button.bind("<ButtonRelease-1>",
                           partial(self.bin_button_callback, div_name))

        remove_button.grid(row=row,
                           column=0,
                           padx=(142, 0),
                           pady=(18, 10),
                           sticky="nw")

        # Key entry
        field_txt = "" if key_action == "None" else key_action
        entry_field = customtkinter.CTkLabel(master=self,
                                             text=field_txt,
                                             image=self.a_button_image,
                                             width=A_BUTTON_SIZE[0],
                                             height=A_BUTTON_SIZE[1],
                                             cursor="hand2")
        entry_field.cget("font").configure(size=17)

        entry_field.bind(
            "<ButtonRelease-1>",
            partial(self.button_click_callback, div_name, entry_field))

        entry_field.grid(row=row,
                         column=0,
                         padx=PAD_X,
                         pady=(10, 10),
                         sticky="nw")

        # Combobox
        drop = customtkinter.CTkOptionMenu(master=self,
                                           values=[gesture_name],
                                           width=DIV_WIDTH,
                                           dynamic_resizing=False,
                                           state="disabled")
        drop.grid(row=row, column=0, padx=PAD_X, pady=(64, 10), sticky="nw")
        drop.grid_remove()
        self.shared_dropdown.register_widget(drop, div_name)

        # Label ?
        tips_label = customtkinter.CTkLabel(master=self,
                                            image=self.help_icon,
                                            compound='right',
                                            text="Gesture size",
                                            text_color="#5E5E5E",
                                            justify='left')
        tips_label.cget("font").configure(size=12)
        tips_label.grid(row=row,
                        column=0,
                        padx=PAD_X,
                        pady=(92, 10),
                        sticky="nw")
        tips_label.grid_remove()
        self.shared_info_balloon.register_widget(tips_label, BALLOON_TXT)

        # Volume bar
        volume_bar = customtkinter.CTkProgressBar(
            master=self,
            width=DIV_WIDTH,
        )

        volume_bar.grid(row=row,
                        column=0,
                        padx=PAD_X,
                        pady=(122, 10),
                        sticky="nw")

        volume_bar.grid_remove()

        # Slider
        slider = customtkinter.CTkSlider(master=self,
                                         from_=1,
                                         to=100,
                                         width=DIV_WIDTH + 10,
                                         number_of_steps=100,
                                         command=partial(
                                             self.slider_drag_callback,
                                             div_name))
        slider.set(thres * 100)
        slider.bind("<Button-1>",
                    partial(self.slider_mouse_down_callback, div_name))
        slider.bind("<ButtonRelease-1>",
                    partial(self.slider_mouse_up_callback, div_name))

        slider.grid(row=row,
                    column=0,
                    padx=PAD_X - 5,
                    pady=(142, 10),
                    sticky="nw")

        slider.grid_remove()

        # Subtle, Exaggerated
        subtle_label = customtkinter.CTkLabel(master=self,
                                              text="Subtle\t\t\t   Exaggerated",
                                              text_color="#868686",
                                              justify=tk.LEFT)
        subtle_label.cget("font").configure(size=11)
        subtle_label.grid(row=row,
                          column=0,
                          padx=PAD_X,
                          pady=(158, 10),
                          sticky="nw")
        subtle_label.grid_remove()

        # Trigger dropdown
        trigger_list = [t.value for t in Trigger]
        trigger_dropdown = customtkinter.CTkOptionMenu(master=self,
                                                       values=trigger_list,
                                                       width=240,
                                                       dynamic_resizing=False,
                                                       state="normal",
                                                       )
        trigger_dropdown.grid(row=row,
                              column=0,
                              padx=PAD_X,
                              pady=(186, 10),
                              sticky="nw")

        trigger_dropdown.grid_remove()

        return {
            "entry_field": entry_field,
            "combobox": drop,
            "tips_label": tips_label,
            "slider": slider,
            "volume_bar": volume_bar,
            "subtle_label": subtle_label,
            "selected_gesture": gesture_name,
            "selected_key_action": key_action,
            "remove_button": remove_button,
            "trigger_dropdown": trigger_dropdown
        }

    def set_new_keyboard_binding(self, div):

        # Remove keybind if set to invalid key
        if (div["selected_gesture"] == "None") or (div["selected_key_action"]
                                                   == "None"):
            logger.info(f"Remove keyboard binding {div['selected_key_action']}")
            ConfigManager().remove_temp_keyboard_binding(
                device="keyboard", gesture=div["selected_gesture"])

            ConfigManager().apply_keyboard_bindings()
            return

        # Set the keybinding
        thres_value = div["slider"].get() / 100
        trigger = Trigger(div["trigger_dropdown"].get())
        ConfigManager().set_temp_keyboard_binding(
            device="keyboard",
            key_action=div["selected_key_action"],
            gesture=div["selected_gesture"],
            threshold=thres_value,
            trigger=trigger)
        ConfigManager().apply_keyboard_bindings()

    def wait_for_key(self, div_name: str, entry_button, keydown: tk.Event):
        """Wait for user to press any key then set the config
        """
        if div_name not in self.divs:
            return
        if self.waiting_div is None:
            return

        div = self.divs[div_name]

        keydown_txt = keydown.keysym.lower() if isinstance(
            keydown, tk.Event) else keydown
        logger.info(f"Key press: <{div_name}> {keydown_txt}")

        occupied_keys = [
            div["entry_field"].cget("text") for div in self.divs.values()
        ]

        # Not valid key
        if (keydown_txt in occupied_keys) or (
                keydown_txt not in shape_list.available_keyboard_keys):
            logger.info(
                f"Key action <{keydown_txt}> not found in available list")
            entry_button.configure(image=self.a_button_image)
            div["selected_key_action"] = "None"
            div["slider"].grid_remove()
            div["combobox"].grid_remove()
            div["volume_bar"].grid_remove()
            div["tips_label"].grid_remove()
            div["subtle_label"].grid_remove()
            div["trigger_dropdown"].grid_remove()
            self.set_new_keyboard_binding(div)

        # Valid key
        else:
            logger.info(f"Found <{keydown_txt}> in available list")
            # Convert key symbol from tkinter to pydirectinput
            pydirectinput_key = shape_list.keyboard_keys[keydown_txt]

            entry_button.configure(text=pydirectinput_key)
            entry_button.configure(image=self.blank_a_button_image)

            div["combobox"].grid()
            div["selected_key_action"] = pydirectinput_key
            self.set_new_keyboard_binding(div)
            if div["selected_gesture"] != "None":
                div["slider"].grid()
                div["combobox"].grid()
                div["volume_bar"].grid()
                div["tips_label"].grid()
                div["subtle_label"].grid()
                div["trigger_dropdown"].grid()

        if self.wait_for_key_bind_id is not None:
            self.waiting_button.unbind("<KeyPress>", self.wait_for_key_bind_id)
        self.refresh_scrollbar()
        self.waiting_div = None
        self.wait_for_key_bind_id = None

    def button_click_callback(self, div_name, entry_button, event):
        """Start wait_for_key after clicked the button      
        """
        # Cancel old waiting function
        if self.waiting_div is not None:
            self.wait_for_key(self.waiting_div, self.waiting_button, "cancel")

        # Start waiting for key press
        self.wait_for_key_bind_id = entry_button.bind(
            "<KeyPress>", partial(self.wait_for_key, div_name, entry_button))
        entry_button.focus_set()

        entry_button.configure(text="")
        entry_button.configure(image=self.a_button_active_image)
        self.waiting_div = div_name
        self.waiting_button = entry_button

    def dropdown_callback(self, div_name: str, target_gesture: str):

        div = self.divs[div_name]

        # Release old item
        if div["selected_gesture"] != target_gesture:
            self.shared_dropdown.enable_item(div["selected_gesture"])
        div["selected_gesture"] = target_gesture
        div["combobox"].set(target_gesture)

        if target_gesture != "None":
            div["slider"].grid()
            div["volume_bar"].grid()
            div["tips_label"].grid()
            div["subtle_label"].grid()
            div["trigger_dropdown"].grid()
        else:
            div["slider"].grid_remove()
            div["volume_bar"].grid_remove()
            div["tips_label"].grid_remove()
            div["subtle_label"].grid_remove()
            div["trigger_dropdown"].grid_remove()

        self.set_new_keyboard_binding(div)
        self.refresh_scrollbar()

    def slider_drag_callback(self, div_name: str, new_value: str):
        """Update value when slider being drag
        """
        self.slider_dragging = True
        new_value = int(new_value)
        if div_name in self.divs:
            div = self.divs[div_name]
            if "entry_var" in div:
                div["entry_var"].set(new_value)

    def slider_mouse_down_callback(self, div_name: str, event):
        self.slider_dragging = True

    def slider_mouse_up_callback(self, div_name: str, event):

        self.slider_dragging = False
        div = self.divs[div_name]
        self.set_new_keyboard_binding(div)

    def update_volume_preview(self):

        bs = FaceMesh().get_blendshapes()

        for div in self.divs.values():

            if div["selected_gesture"] == "None":
                continue

            bs_idx = shape_list.blendshape_indices[div["selected_gesture"]]
            bs_value = bs[bs_idx]
            div["volume_bar"].set(bs_value)

            slider_value = div["slider"].get() / 100
            if bs_value > slider_value:
                div["volume_bar"].configure(progress_color=GREEN)  # green
            else:
                div["volume_bar"].configure(progress_color=YELLOW)  # yellow

    def frame_loop(self):
        if self.is_destroyed:
            return

        if self.is_active:
            self.update_volume_preview()
            self.after(50, self.frame_loop)
        else:
            return

    def inner_refresh_profile(self):
        """Refresh the page divs to match the new profile
        """
        # Remove old divs
        self.next_empty_row = 0
        for div_name, div in self.divs.items():
            self.remove_div(div_name)
        self.divs = {}

        # Create new divs form the new profile
        self.load_initial_keybindings()

    def enter(self):
        super().enter()
        self.after(1, self.frame_loop)

    def leave(self):
        super().leave()
        self.wait_for_key(self.waiting_div, self.waiting_button, "cancel")


class PageKeyboard(SafeDisposableFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.is_active = False
        self.grid_propagate(False)
        self.bind_id_leave = None

        # Top label.
        self.top_label = customtkinter.CTkLabel(master=self,
                                                text="Keyboard binding")
        self.top_label.cget("font").configure(size=24)
        self.top_label.grid(row=0,
                            column=0,
                            padx=20,
                            pady=5,
                            sticky="nw",
                            columnspan=1)

        # Description.
        des_txt = "Select a facial gesture that you would like to bind to a specific keyboard key. Sensitivity allows you to control the extent to which you need to gesture to trigger the keyboard key press"
        des_label = customtkinter.CTkLabel(master=self,
                                           text=des_txt,
                                           wraplength=300,
                                           justify=tk.LEFT)  #
        des_label.cget("font").configure(size=14)
        des_label.grid(row=1, column=0, padx=20, pady=(10, 40), sticky="nw")

        # Inner frame
        self.inner_frame = FrameSelectKeyboard(
            self, logger_name="FrameSelectKeyboard")
        self.inner_frame.grid(row=3, column=0, padx=5, pady=5, sticky="nswe")

        # Add binding button
        self.add_binding_button = customtkinter.CTkButton(
            master=self,
            text="+ Add binding",
            fg_color="white",
            text_color=BLUE,
            command=self.inner_frame.add_blank_div)
        self.add_binding_button.grid(row=2,
                                     column=0,
                                     padx=5,
                                     pady=5,
                                     sticky="nw")

    def enter(self):
        super().enter()
        self.inner_frame.enter()

        # Hide dropdown when mouse leave the frame
        self.bind_id_leave = self.bind(
            "<Leave>", self.inner_frame.shared_dropdown.hide_dropdown)

    def refresh_profile(self):
        self.inner_frame.inner_refresh_profile()

    def leave(self):
        super().leave()
        self.inner_frame.leave()
        self.unbind("<Leave>", self.bind_id_leave)

        self.inner_frame.shared_dropdown.hide_dropdown()

    def destroy(self):
        super().destroy()
        self.inner_frame.destroy()
