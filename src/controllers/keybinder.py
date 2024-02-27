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
from src.utils.Trigger import Trigger

logger = logging.getLogger("Keybinder")

# disable lag
pydirectinput.PAUSE = 0
pydirectinput.FAILSAFE = False


class Keybinder(metaclass=Singleton):

    def __init__(self) -> None:
        self.delay_count = None
        self.key_states = None
        self.schedule_toggle_off = {}
        self.schedule_toggle_on = {}
        self.monitors = None
        self.screen_h = None
        self.screen_w = None
        logger.info("Initialize Keybinder singleton")
        self.top_count = 0
        self.start_hold_ts = {}
        self.holding = {}
        self.is_started = False
        self.last_know_keybindings = {}
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
        """Re-initializes the state of the keybinder.
           If new keybindings are added.
        """
        # keep states for all registered keys.
        self.key_states = {}
        self.start_hold_ts = {}
        for _, v in (ConfigManager().mouse_bindings |
                     ConfigManager().keyboard_bindings).items():
            state_name = v[0]+"_"+v[1]
            self.key_states[state_name] = False
            self.schedule_toggle_off[state_name] = False
            self.schedule_toggle_on[state_name] = True
            self.start_hold_ts[state_name] = math.inf
            self.holding[state_name] = False

        self.last_know_keybindings = copy.deepcopy(
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

    def get_current_monitor(self) -> int:

        x, y = pydirectinput.position()
        for mon_id, mon in enumerate(self.monitors):
            if x >= mon["x1"] and x <= mon["x2"] and y >= mon[
                "y1"] and y <= mon["y2"]:
                return mon_id
        # raise Exception("Monitor not found")
        return 0

    def meta_action(self, val, action, threshold, is_active: bool) -> None:
        state_name = "meta_" + action

        if action == "pause":

            if (val > threshold) and (self.key_states[state_name] is False):
                mon_id = self.get_current_monitor()
                if mon_id is None:
                    return

                self.toggle_active()

                self.key_states[state_name] = True
            elif (val < threshold) and (self.key_states[state_name] is True):
                self.key_states[state_name] = False

        if is_active:

            if action == "reset":
                if (val > threshold) and (self.key_states[state_name] is
                                      False):
                    mon_id = self.get_current_monitor()
                    if mon_id is None:
                        return

                    pydirectinput.moveTo(
                        self.monitors[mon_id]["center_x"],
                        self.monitors[mon_id]["center_y"])
                    self.key_states[state_name] = True
                elif (val < threshold) and (self.key_states[state_name] is
                                        True):
                    self.key_states[state_name] = False

            elif action == "cycle":
                if (val > threshold) and (self.key_states[state_name] is
                                      False):
                    mon_id = self.get_current_monitor()
                    next_mon_id = (mon_id + 1) % len(self.monitors)
                    pydirectinput.moveTo(
                        self.monitors[next_mon_id]["center_x"],
                        self.monitors[next_mon_id]["center_y"])
                    self.key_states[state_name] = True
                elif (val < threshold) and (self.key_states[state_name] is
                                        True):
                    self.key_states[state_name] = False

    def mouse_action(self, val, action, threshold, mode) -> None:
        state_name = "mouse_" + action

        if mode == Trigger.SINGLE:
            if val > threshold:
                if self.key_states[state_name] is False:
                    pydirectinput.click(button=action)
                    self.key_states[state_name] = True
            if val < threshold:
                self.key_states[state_name] = False

        elif mode == Trigger.HOLD:
            if (val > threshold) and (self.key_states[state_name] is False):
                pydirectinput.mouseDown(button=action)
                self.key_states[state_name] = True

            elif (val < threshold) and (self.key_states[state_name] is True):
                pydirectinput.mouseUp(button=action)
                self.key_states[state_name] = False

        elif mode == Trigger.DYNAMIC:
            if val > threshold:
                if self.key_states[state_name] is False:
                    pydirectinput.click(button=action)
                    self.start_hold_ts[state_name] = time.time()
                    self.key_states[state_name] = True

                if self.holding[state_name] is False and (
                        ((time.time() - self.start_hold_ts[state_name]) * 1000) >=
                        ConfigManager().config["hold_trigger_ms"]):
                    pydirectinput.mouseDown(button=action)
                    self.holding[state_name] = True

            elif (val < threshold) and (self.key_states[state_name] is True):

                self.key_states[state_name] = False

                if self.holding[state_name]:
                    pydirectinput.mouseUp(button=action)
                    self.holding[state_name] = False
                    self.start_hold_ts[state_name] = math.inf

        elif mode == Trigger.TOGGLE:
            if val > threshold:
                if self.key_states[state_name] is False:
                    if self.schedule_toggle_on[state_name] is True:
                        pydirectinput.mouseDown(button=action)
                        self.key_states[state_name] = True

                if self.key_states[state_name] is True:
                    if self.schedule_toggle_off[state_name] is True:
                        pydirectinput.mouseUp(button=action)
                        self.key_states[state_name] = False

            if val < threshold:
                if self.key_states[state_name] is True:
                    self.schedule_toggle_off[state_name] = True
                    self.schedule_toggle_on[state_name] = False
                if self.key_states[state_name] is False:
                    self.schedule_toggle_on[state_name] = True
                    self.schedule_toggle_off[state_name] = False

        elif mode == Trigger.RAPID:
            if val > threshold:
                if self.key_states[state_name] is False:
                    pydirectinput.click(button=action)
                    self.key_states[state_name] = True
                    self.start_hold_ts[state_name] = time.time()

                if self.key_states[state_name] is True:
                    if (((time.time() - self.start_hold_ts[state_name]) * 1000)
                            >= ConfigManager().config["rapid_fire_interval_ms"]):
                        pydirectinput.click(button=action)
                        self.holding[state_name] = True
                        self.start_hold_ts[state_name] = time.time()

            if val < threshold:
                if self.key_states[state_name] is True:
                    self.key_states[state_name] = False
                    self.start_hold_ts[state_name] = math.inf

    def keyboard_action(self, val, keysym, threshold, mode):

        state_name = "keyboard_" + keysym

        if mode == Trigger.SINGLE:
            if val > threshold:
                if self.key_states[state_name] is False:
                    pydirectinput.press(keys=keysym)
                    self.key_states[state_name] = True
            if val < threshold:
                self.key_states[state_name] = False

        elif mode == Trigger.HOLD:
            if (val > threshold) and (self.key_states[state_name] is False):
                pydirectinput.keyDown(key=keysym)
                self.key_states[state_name] = True

            elif (val < threshold) and (self.key_states[state_name] is True):
                pydirectinput.keyUp(key=keysym)
                self.key_states[state_name] = False

        elif mode == Trigger.DYNAMIC:
            if val > threshold:
                if self.key_states[state_name] is False:
                    pydirectinput.press(keys=keysym)
                    self.start_hold_ts[state_name] = time.time()
                    self.key_states[state_name] = True

                if self.holding[state_name] is False and (
                        ((time.time() - self.start_hold_ts[state_name]) * 1000) >=
                        ConfigManager().config["hold_trigger_ms"]):
                    pydirectinput.keyDown(key=keysym)
                    self.holding[state_name] = True

            elif (val < threshold) and (self.key_states[state_name] is True):

                self.key_states[state_name] = False

                if self.holding[state_name]:
                    pydirectinput.keyUp(key=keysym)
                    self.holding[state_name] = False
                    self.start_hold_ts[state_name] = math.inf

        elif mode == Trigger.TOGGLE:
            if val > threshold:
                if self.key_states[state_name] is False:
                    if self.schedule_toggle_on[state_name] is True:
                        pydirectinput.keyDown(key=keysym)
                        self.key_states[state_name] = True

                if self.key_states[state_name] is True:
                    if self.schedule_toggle_off[state_name] is True:
                        pydirectinput.keyUp(key=keysym)
                        self.key_states[state_name] = False

            if val < threshold:
                if self.key_states[state_name] is True:
                    self.schedule_toggle_off[state_name] = True
                    self.schedule_toggle_on[state_name] = False
                if self.key_states[state_name] is False:
                    self.schedule_toggle_on[state_name] = True
                    self.schedule_toggle_off[state_name] = False

        elif mode == Trigger.RAPID:
            if val > threshold:
                if self.key_states[state_name] is False:
                    pydirectinput.press(keys=keysym)
                    self.key_states[state_name] = True
                    self.start_hold_ts[state_name] = time.time()

                if self.key_states[state_name] is True:
                    if (((time.time() - self.start_hold_ts[state_name]) * 1000)
                            >= ConfigManager().config["rapid_fire_interval_ms"]):
                        pydirectinput.press(keys=keysym)
                        self.holding[state_name] = True
                        self.start_hold_ts[state_name] = time.time()

            if val < threshold:
                if self.key_states[state_name] is True:
                    self.key_states[state_name] = False
                    self.start_hold_ts[state_name] = math.inf

    def act(self, blendshape_values) -> None:
        """Trigger devices action base on blendshape values

        Args:
            blendshape_values (npt.ArrayLike): blendshape values from tflite model

        Returns:
            dict: debug states
        """

        if blendshape_values is None:
            return

        if (ConfigManager().mouse_bindings |
            ConfigManager().keyboard_bindings) != self.last_know_keybindings:
            self.init_states()

        for shape_name, v in (ConfigManager().mouse_bindings |
                              ConfigManager().keyboard_bindings).items():
            if shape_name not in shape_list.blendshape_names:
                continue

            device, action, threshold, mode = v
            mode = Trigger(mode.lower())
            # Get blendshape value
            idx = shape_list.blendshape_indices[shape_name]
            val = blendshape_values[idx]

            if device == "meta":
                self.meta_action(val, action, threshold, self.is_active.get())

            if self.is_active.get():

                if device == "mouse":
                    self.mouse_action(val, action, threshold, mode)

                elif device == "keyboard":
                    self.keyboard_action(val, action, threshold, mode)

    def set_active(self, flag: bool) -> None:
        self.is_active.set(flag)
        if flag:
            self.delay_count = 0

    def toggle_active(self):
        logging.info("Toggle active")
        current_state = self.is_active.get()
        self.set_active(not current_state)

    def destroy(self):
        """Destroy the keybinder"""
        logger.info("releasing all keys...")
        for state_name in self.key_states:
            # TODO: too many python shenanigans. Might break if you look wrong at it
            device, action = state_name.split("_")
            if device == "mouse":
                logger.info(f"releasing {state_name}")
                pydirectinput.mouseUp(button=action)
            if device == "keyboard":
                logger.info(f"releasing {state_name}")
                pydirectinput.keyUp(key=action)
            elif device == "meta":
                pass

        return
