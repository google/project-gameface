
import copy
import logging
import math
import time

import pydirectinput
import win32api
import tkinter as tk

import src.shape_list as shape_list
from src.config_manager import ConfigManager
from src.singleton_meta import Singleton

logger = logging.getLogger("Keybinder")

# disable lag
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False


class Keybinder(metaclass=Singleton):

    def __init__(self) -> None:
        logger.info("Intialize Keybinder singleton")
        self.top_count = 0
        self.triggered = False
        self.start_hold_ts = math.inf
        self.holding = False
        self.is_started = False
        self.last_know_keybinds = {}
        self.is_active = None

    def start(self):
        if not self.is_started:
            logger.info("Start Keybinder singleton")
            self.init_states()
            self.screen_w, self.screen_h = pydirectinput.size()
            self.monitors = self.get_monitors()
            self.is_started = True

            self.is_active = tk.BooleanVar()
            self.is_active.set(ConfigManager().config["auto_play"])

    def init_states(self) -> None:
        """Re initializes the state of the keybinder.
           If new keybinds are added.
        """
        # keep states for all registered keys.
        self.key_states = {}
        for _, v in (ConfigManager().mouse_bindings |
                     ConfigManager().keyboard_bindings).items():
            self.key_states[v[0] + "_" + v[1]] = False
        self.key_states["holding"] = False
        self.last_know_keybinds = copy.deepcopy(
            (ConfigManager().mouse_bindings |
             ConfigManager().keyboard_bindings))

    def get_monitors(self) -> list[dict]:
        out_list = []
        monitors = win32api.EnumDisplayMonitors()
        for i, (_, _, loc) in enumerate(monitors):
            mon_info = {}
            mon_info["id"] = i
            mon_info["x1"] = loc[0]
            mon_info["y1"] = loc[1]
            mon_info["x2"] = loc[2]
            mon_info["y2"] = loc[3]
            mon_info["center_x"] = (loc[0] + loc[2]) // 2
            mon_info["center_y"] = (loc[1] + loc[3]) // 2
            out_list.append(mon_info)

        return out_list

    def get_curr_monitor(self):

        x, y = pydirectinput.position()
        for mon_id, mon in enumerate(self.monitors):
            if x >= mon["x1"] and x <= mon["x2"] and y >= mon[
                    "y1"] and y <= mon["y2"]:
                return mon_id
        #raise Exception("Monitor not found")
        return 0

    def mouse_action(self, val, action, thres, mode) -> None:
        state_name = "mouse_" + action

        mode = "hold" if self.key_states["holding"] else "single"

        if mode == "hold":
            if (val > thres) and (self.key_states[state_name] is False):
                pydirectinput.mouseDown(action)

                self.key_states[state_name] = True

            elif (val < thres) and (self.key_states[state_name] is True):
                pydirectinput.mouseUp(action)
                self.key_states[state_name] = False

        elif mode == "single":
            if (val > thres):
                if not self.key_states[state_name]:
                    pydirectinput.click(button=action)
                    self.start_hold_ts = time.time()

                self.key_states[state_name] = True

                if not self.holding and (
                    ((time.time() - self.start_hold_ts) * 1000) >=
                        ConfigManager().config["hold_trigger_ms"]):

                    pydirectinput.mouseDown(button=action)
                    self.holding = True

            elif (val < thres) and (self.key_states[state_name] is True):

                self.key_states[state_name] = False

                if self.holding:
                    pydirectinput.mouseUp(button=action)
                    self.holding = False
                    self.start_hold_ts = math.inf

    def keyboard_action(self, val, keysym, thres, mode):

        state_name = "keyboard_" + keysym

        if (self.key_states[state_name] is False) and (val > thres):
            pydirectinput.keyDown(keysym)
            self.key_states[state_name] = True

        elif (self.key_states[state_name] is True) and (val < thres):
            pydirectinput.keyUp(keysym)
            self.key_states[state_name] = False

    def act(self, blendshape_values) -> dict:
        """Trigger devices action base on blendshape values

        Args:
            blendshape_values (npt.ArrayLike): blendshape values from tflite model

        Returns:
            dict: debug states
        """

        if blendshape_values is None:
            return

        if (ConfigManager().mouse_bindings |
                ConfigManager().keyboard_bindings) != self.last_know_keybinds:
            self.init_states()

        for shape_name, v in (ConfigManager().mouse_bindings |
                              ConfigManager().keyboard_bindings).items():
            if shape_name not in shape_list.blendshape_names:
                continue
            device, action, thres, mode = v

            # Get blendshape value
            idx = shape_list.blendshape_indices[shape_name]
            val = blendshape_values[idx]

            if (device == "mouse") and (action == "pause"):
                state_name = "mouse_" + action

                if (val > thres) and (self.key_states[state_name] is False):
                    mon_id = self.get_curr_monitor()
                    if mon_id is None:
                        return

                    self.toggle_active()

                    self.key_states[state_name] = True
                elif (val < thres) and (self.key_states[state_name] is True):
                    self.key_states[state_name] = False

            elif self.is_active.get():

                if device == "mouse":

                    if action == "reset":
                        state_name = "mouse_" + action
                        if (val > thres) and (self.key_states[state_name] is
                                              False):
                            mon_id = self.get_curr_monitor()
                            if mon_id is None:
                                return

                            pydirectinput.moveTo(
                                self.monitors[mon_id]["center_x"],
                                self.monitors[mon_id]["center_y"])
                            self.key_states[state_name] = True
                        elif (val < thres) and (self.key_states[state_name] is
                                                True):
                            self.key_states[state_name] = False

                    elif action == "cycle":
                        state_name = "mouse_" + action
                        if (val > thres) and (self.key_states[state_name] is
                                              False):
                            mon_id = self.get_curr_monitor()
                            next_mon_id = (mon_id + 1) % len(self.monitors)
                            pydirectinput.moveTo(
                                self.monitors[next_mon_id]["center_x"],
                                self.monitors[next_mon_id]["center_y"])
                            self.key_states[state_name] = True
                        elif (val < thres) and (self.key_states[state_name] is
                                                True):
                            self.key_states[state_name] = False

                    else:
                        self.mouse_action(val, action, thres, mode)

                elif device == "keyboard":
                    self.keyboard_action(val, action, thres, mode)

    def set_active(self, flag: bool) -> None:
        self.is_active.set(flag)
        if flag:
            self.delay_count = 0

    def toggle_active(self):
        logging.info("Toggle active")
        curr_state = self.is_active.get()
        self.set_active(not curr_state)

    def destroy(self):
        """Destroy the keybinder"""
        return
