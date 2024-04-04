import tkinter as tk
from functools import partial

import customtkinter
from PIL import Image

import src.shape_list as shape_list
from src.config_manager import ConfigManager
from src.detectors import FaceMesh
from src.gui.balloon import Balloon
from src.gui.dropdown import Dropdown
from src.gui.frames.safe_disposable_frame import SafeDisposableFrame
from src.utils.Trigger import Trigger

MAX_ROWS = 2
HELP_ICON_SIZE = (18, 18)
DIV_WIDTH = 240
DEFAULT_TRIGGER_TYPE = "dynamic"
GREEN = "#34A853"
YELLOW = "#FABB05"

BALLOON_TXT = "Set how prominent your gesture has\nto be in order to trigger the action"


class FrameSelectGesture(SafeDisposableFrame):

    def __init__(
            self,
            master,
            **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.is_active = False

        self.grid_rowconfigure(MAX_ROWS, weight=1)
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

        # Divs
        self.divs = self.create_divs(shape_list.available_actions_keys,
                                     shape_list.available_gestures_keys)
        self.load_initial_keybindings()
        self.slider_dragging = False

    def set_div_inactive(self, div):
        none_gesture = shape_list.available_gestures_keys[0]
        div["selected_gesture"] = none_gesture
        div["combobox"].set(none_gesture)
        div["slider"].grid_remove()
        div["tips_label"].grid_remove()
        div["subtle_label"].grid_remove()
        div["slider"].grid_remove()
        div["volume_bar"].grid_remove()
        div["trigger_dropdown"].set(DEFAULT_TRIGGER_TYPE)
        div["trigger_dropdown"].grid_remove()

    def set_div_active(self, div, gesture_name, thres, trigger):
        div["selected_gesture"] = gesture_name
        div["combobox"].set(gesture_name)
        div["slider"].set(int(thres * 100))
        div["slider"].configure(state="normal")
        div["trigger_dropdown"].configure(state="normal")
        div["trigger_dropdown"].set(trigger)

        div["tips_label"].grid()
        div["subtle_label"].grid()
        div["slider"].grid()
        div["volume_bar"].grid()
        div["trigger_dropdown"].grid()

    def load_initial_keybindings(self):
        """Load default from config and set the UI
        """

        for div_name, div in self.divs.items():
            self.set_div_inactive(div)

        for gesture_name, (
                device, action_key, thres,
                trigger_type) in ConfigManager().mouse_bindings.items():
            if [device, action_key] not in shape_list.available_actions_values:
                continue
            action_idx = shape_list.available_actions_values.index(
                [device, action_key])
            target_action_name = shape_list.available_actions_keys[action_idx]
            div = self.divs[target_action_name]
            self.set_div_active(div, gesture_name, thres, trigger_type)
            self.shared_dropdown.disable_item(gesture_name)
        self.shared_dropdown.refresh_items()

    def create_divs(self, action_list: list, gesture_list: list):
        out_dict = {}

        for idx, action_name in enumerate(action_list):
            row = idx % (MAX_ROWS + 1)
            column = idx // (MAX_ROWS + 1)

            # Action label
            label = customtkinter.CTkLabel(master=self,
                                           text=action_name,
                                           height=200,
                                           width=300,
                                           anchor='nw',
                                           justify=tk.LEFT)
            label.cget("font").configure(weight='bold')
            label.grid(row=row,
                       column=column,
                       padx=(20, 20),
                       pady=(0, 0),
                       sticky="nw")

            # Combobox
            drop = customtkinter.CTkOptionMenu(master=self,
                                               values=[gesture_list[0]],
                                               width=240,
                                               dynamic_resizing=False,
                                               state="disabled")
            drop.grid(row=row,
                      column=column,
                      padx=(20, 20),
                      pady=(28, 10),
                      sticky="nw")
            self.shared_dropdown.register_widget(drop, action_name)

            # Label ?
            tips_label = customtkinter.CTkLabel(master=self,
                                                image=self.help_icon,
                                                compound='right',
                                                text="Gesture size",
                                                text_color="#5E5E5E",
                                                justify='left')
            tips_label.cget("font").configure(size=12)
            tips_label.grid(row=row,
                            column=column,
                            padx=(20, 20),
                            pady=(62, 10),
                            sticky="nw")
            tips_label.grid_remove()
            self.shared_info_balloon.register_widget(tips_label, BALLOON_TXT)

            # Volume bar
            volume_bar = customtkinter.CTkProgressBar(
                master=self,
                width=240,
            )
            volume_bar.grid(row=row,
                            column=column,
                            padx=(20, 20),
                            pady=(92, 10),
                            sticky="nw")
            volume_bar.grid_remove()

            # Slider
            slider = customtkinter.CTkSlider(master=self,
                                             from_=1,
                                             to=100,
                                             width=250,
                                             number_of_steps=100,
                                             command=partial(
                                                 self.slider_drag_callback,
                                                 action_name))
            slider.bind("<Button-1>",
                        partial(self.slider_mouse_down_callback, action_name))
            slider.bind("<ButtonRelease-1>",
                        partial(self.slider_mouse_up_callback, action_name))
            slider.configure(state="disabled", hover=False)
            slider.grid(row=row,
                        column=column,
                        padx=(15, 20),
                        pady=(112, 10),
                        sticky="nw")
            slider.grid_remove()

            # Subtle, Exaggerated
            subtle_label = customtkinter.CTkLabel(
                master=self,
                text="Subtle\t\t\t   Exaggerated",
                text_color="#868686",
                justify=tk.LEFT)
            subtle_label.cget("font").configure(size=11)
            subtle_label.grid(row=row,
                              column=column,
                              padx=(20, 20),
                              pady=(128, 10),
                              sticky="nw")
            subtle_label.grid_remove()

            # Trigger dropdown
            trigger_list = [t.value for t in Trigger]
            trigger_dropdown = customtkinter.CTkOptionMenu(master=self,
                                                           values=trigger_list,
                                                           width=240,
                                                           dynamic_resizing=False,
                                                           state="disabled"
                                                           )
            trigger_dropdown.grid(row=row,
                                  column=column,
                                  padx=(20, 20),
                                  pady=(156, 10),
                                  sticky="nw")

            out_dict[action_name] = {
                "label": label,
                "combobox": drop,
                "tips_label": tips_label,
                "slider": slider,
                "volume_bar": volume_bar,
                "subtle_label": subtle_label,
                "selected_gesture": gesture_list[0],
                "trigger_dropdown": trigger_dropdown
            }

        return out_dict

    def slider_drag_callback(self, caller_name: str, slider_value: str):
        self.slider_dragging = True

    def slider_mouse_down_callback(self, caller_name: str, event):
        self.slider_dragging = True

    def slider_mouse_up_callback(self, caller_name: str, event):
        self.slider_dragging = False
        div = self.divs[caller_name]
        target_device, target_action = shape_list.available_actions[caller_name]

        # change int [0,100] to float [0,1]
        thres_value = div["slider"].get() / 100

        trigger = Trigger(div["trigger_dropdown"].get())


        ConfigManager().set_temp_mouse_binding(
            div["selected_gesture"],
            device=target_device,
            action=target_action,
            threshold=thres_value,
            trigger=trigger)
        ConfigManager().apply_mouse_bindings()

    def dropdown_callback(self, caller_name: str, target_gesture: str):
        div = self.divs[caller_name]

        # Release old item
        if div["selected_gesture"] != target_gesture:
            self.shared_dropdown.enable_item(div["selected_gesture"])
        div["selected_gesture"] = target_gesture
        div["combobox"].set(target_gesture)

        # Set keybind
        target_device, target_action = shape_list.available_actions[caller_name]

        # get float [0,1] value
        if target_gesture != "None":
            div["slider"].configure(state="normal")
            div["slider"].grid()
            div["volume_bar"].grid()
            div["tips_label"].grid()
            div["subtle_label"].grid()
            div["trigger_dropdown"].grid()
            thres_value = div["slider"].get() / 100
            trigger = Trigger(div["trigger_dropdown"].get())

            ConfigManager().set_temp_mouse_binding(
                target_gesture,
                device=target_device,
                action=target_action,
                threshold=thres_value,
                trigger=trigger)

        # Remove keybind if "None"
        else:
            div["slider"].configure(state="disabled")
            div["slider"].grid_remove()
            div["volume_bar"].grid_remove()
            div["tips_label"].grid_remove()
            div["subtle_label"].grid_remove()
            div["trigger_dropdown"].grid_remove()
            ConfigManager().remove_temp_mouse_binding(device=target_device,
                                                      action=target_action)

        ConfigManager().apply_mouse_bindings()

    def update_volume_preview(self):

        bs = FaceMesh().get_blendshapes()

        for div_name, div in self.divs.items():

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
        # Create new divs form the new profile
        self.load_initial_keybindings()

    def enter(self):
        super().enter()
        # self.load_initial_keybindings()
        self.after(1, self.frame_loop)

    def leave(self):
        super().leave()


class PageSelectGestures(SafeDisposableFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.is_active = False
        self.grid_propagate(False)
        self.bind_id_leave = None

        # Top label.
        self.top_label = customtkinter.CTkLabel(master=self,
                                                text="Mouse binding")
        self.top_label.cget("font").configure(size=24)
        self.top_label.grid(row=0,
                            column=0,
                            padx=20,
                            pady=5,
                            sticky="nw",
                            columnspan=1)

        # Description.
        des_txt = "Select a facial gesture that you would like to bind to a specific mouse action. Sensitivity allows you to control  the extent to which you need to gesture to trigger the mouse action"
        des_label = customtkinter.CTkLabel(master=self,
                                           text=des_txt,
                                           wraplength=300,
                                           justify=tk.LEFT)  #
        des_label.cget("font").configure(size=14)
        des_label.grid(row=1, column=0, padx=20, pady=10, sticky="nw")

        # Inner frame
        self.inner_frame = FrameSelectGesture(self,
                                              logger_name="FrameSelectGesture")
        self.inner_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nw")

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
