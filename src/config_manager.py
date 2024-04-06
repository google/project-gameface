import copy
import json
import logging
import shutil
import time
import tkinter as tk
import os
from pathlib import Path

from src.singleton_meta import Singleton
from src.task_killer import TaskKiller
from src.utils.Trigger import Trigger

VERSION = "0.5.0"

DEFAULT_JSON = Path(f"C:/Users/{os.getlogin()}/Grimassist/configs/default.json")
BACKUP_PROFILE = Path(f"C:/Users/{os.getlogin()}/Grimassist/configs/default")

logger = logging.getLogger("ConfigManager")

config_dir = f"C:/Users/{os.getlogin()}/Grimassist/configs/"
default_dir = os.path.join(config_dir, "default")

# Create the main config directory if it doesn't exist
if not os.path.isdir(config_dir):
    os.makedirs(config_dir, exist_ok=True)
    shutil.copytree("configs", config_dir, dirs_exist_ok=True)

# Create the default directory inside the config directory if it doesn't exist
if not os.path.isdir(default_dir):
    os.mkdir(default_dir)

if not os.path.isdir(f"C:/Users/{os.getlogin()}/Grimassist/configs/"):
    shutil.copytree("configs", f"C:/Users/{os.getlogin()}/Grimassist/configs/")
    os.mkdir(f"C:/Users/{os.getlogin()}/Grimassist/configs/")

if not os.path.isdir(f"C:/Users/{os.getlogin()}/Grimassist/configs/default"):
    os.mkdir(f"C:/Users/{os.getlogin()}/Grimassist/configs/default")


class ConfigManager(metaclass=Singleton):

    def __init__(self):
        self.temp_keyboard_bindings = None
        self.temp_mouse_bindings = None
        self.temp_config = None
        self.keyboard_bindings = None
        self.mouse_bindings = None
        logger.info("Initialize ConfigManager singleton")
        self.version = VERSION
        self.unsave_configs = False
        self.unsave_mouse_bindings = False
        self.unsave_keyboard_bindings = False
        self.config = None

        # Load config
        self.current_profile_path = None
        self.current_profile_name = tk.StringVar()
        self.is_started = False

        self.profiles = self.list_profile()

    def start(self):
        if not self.is_started:
            logger.info("Start ConfigManager singleton")
            if not DEFAULT_JSON.is_file():
                logger.critical(f"Missing {DEFAULT_JSON}, exit program...")
                TaskKiller().exit()

            try:
                with open(DEFAULT_JSON) as f:
                    self.load_profile(json.load(f)["default"])
            except Exception as e:
                logging.error(e)
                logging.error(
                    f"Failed to load default profile {DEFAULT_JSON}, using first profile instead."
                )
                self.load_profile(self.list_profile()[0])
            self.is_started = True

    def list_profile(self) -> list:
        profile_dirs = []
        for dir in DEFAULT_JSON.parent.glob("*"):
            if dir.is_dir():
                profile_dirs.append(dir.name)
        logger.info(profile_dirs)
        return profile_dirs

    def remove_profile(self, profile_name):
        logger.info(f"Remove profile {profile_name}")
        shutil.rmtree(Path(DEFAULT_JSON.parent, profile_name))
        self.profiles.remove(profile_name)
        logger.info(f"Current profiles: {self.profiles}")

    def add_profile(self):
        # Random name base on local timestamp
        new_profile_name = "profile_z" + str(hex(int(time.time() * 1000)))[2:]
        logger.info(f"Add profile {new_profile_name}")
        shutil.copytree(BACKUP_PROFILE,
                        Path(DEFAULT_JSON.parent, new_profile_name))
        self.profiles.append(new_profile_name)
        logger.info(f"Current profiles: {self.profiles}")

    def rename_profile(self, old_profile_name, new_profile_name):
        logger.info(f"Rename profile {old_profile_name} to {new_profile_name}")
        shutil.move(Path(DEFAULT_JSON.parent, old_profile_name),
                    Path(DEFAULT_JSON.parent, new_profile_name))
        self.profiles.remove(old_profile_name)
        self.profiles.append(new_profile_name)

        if self.current_profile_name.get() == old_profile_name:
            self.current_profile_name.set(new_profile_name)



    def load_profile(self, profile_name: str):
        profile_path = Path(DEFAULT_JSON.parent, profile_name)
        logger.info(f"Loading profile: {profile_path}")

        cursor_config_file = Path(profile_path, "cursor.json")
        mouse_bindings_file = Path(profile_path, "mouse_bindings.json")
        keyboard_bindings_file = Path(profile_path, "keyboard_bindings.json")

        if (not cursor_config_file.is_file()) or (
                not mouse_bindings_file.is_file()) or (
                    not keyboard_bindings_file.is_file()):
            logger.critical(
                f"{profile_path.as_posix()} Invalid configuration files or missing files, exit program..."
            )
            raise FileNotFoundError

        # Load cursor config
        with open(cursor_config_file) as f:
            self.config = json.load(f)

        # Load mouse bindings
        with open(mouse_bindings_file) as f:
            self.mouse_bindings = json.load(f)

        # Load keyboard bindings
        with open(keyboard_bindings_file) as f:
            self.keyboard_bindings = json.load(f)

        self.temp_config = copy.deepcopy(self.config)
        self.temp_mouse_bindings = copy.deepcopy(self.mouse_bindings)
        self.temp_keyboard_bindings = copy.deepcopy(self.keyboard_bindings)

        self.current_profile_path = profile_path
        self.current_profile_name.set(profile_name)

    def switch_profile(self, profile_name: str):
        logger.info(f"Switching to profile: {profile_name}")
        self.load_profile(profile_name)
        with open(DEFAULT_JSON, "w") as f:
            json.dump({"default": profile_name}, f)

    # ------------------------------- BASIC CONFIG ------------------------------- #

    def set_temp_config(self, field: str, value):
        logger.info(f"Setting {field} to {value}")
        self.temp_config[field] = value
        self.unsave_configs = True

    def write_config_file(self):
        cursor_config_file = Path(self.current_profile_path, "cursor.json")
        logger.info(f"Writing config file {cursor_config_file}")
        with open(cursor_config_file, 'w') as f:
            json.dump(self.config, f, indent=4, separators=(', ', ': '))

    def apply_config(self):
        logger.info("Applying config")
        self.config = copy.deepcopy(self.temp_config)
        self.write_config_file()
        self.unsave_configs = False

    # ------------------------------ MOUSE BINDINGS CONFIG ----------------------------- #

    def set_temp_mouse_binding(self, gesture, device: str, action: str,
                               threshold: float, trigger: Trigger):

        logger.info(
            "setting keybind for gesture: %s, device: %s, key: %s, threshold: %s, trigger: %s",
            gesture, device, action, threshold, trigger.value)

        # Remove duplicate keybindings
        self.remove_temp_mouse_binding(device, action)

        # Assign
        self.temp_mouse_bindings[gesture] = [
            device, action, float(threshold), trigger.value
        ]
        self.unsave_mouse_bindings = True

    def remove_temp_mouse_binding(self, device: str, action: str):
        logger.info(
            f"remove_temp_mouse_binding for device: {device}, key: {action}")
        out_keybindings = {}
        for key, vals in self.temp_mouse_bindings.items():
            if (device == vals[0]) and (action == vals[1]):
                continue
            out_keybindings[key] = vals
        self.temp_mouse_bindings = out_keybindings
        self.unsave_mouse_bindings = True

    def apply_mouse_bindings(self):
        logger.info("Applying keybindings")
        self.mouse_bindings = copy.deepcopy(self.temp_mouse_bindings)
        self.write_mouse_bindings_file()
        self.unsave_mouse_bindings = False

    def write_mouse_bindings_file(self):
        mouse_bindings_file = Path(self.current_profile_path,
                                   "mouse_bindings.json")
        logger.info(f"Writing keybindings file {mouse_bindings_file}")

        with open(mouse_bindings_file, 'w') as f:
            out_json = dict(sorted(self.mouse_bindings.items()))
            json.dump(out_json, f, indent=4, separators=(', ', ': '))

    # ------------------------------ KEYBOARD BINDINGS CONFIG ----------------------------- #

    def set_temp_keyboard_binding(self, device: str, key_action: str,
                                  gesture: str, threshold: float,
                                  trigger: Trigger):
        logger.info(
            "setting keybind for gesture: %s, device: %s, key: %s, threshold: %s, trigger: %s",
            gesture, device, key_action, threshold, trigger.value)

        # Remove duplicate keybindings
        self.remove_temp_keyboard_binding(device, key_action, gesture)

        # Assign
        self.temp_keyboard_bindings[gesture] = [
            device, key_action,
            float(threshold), trigger.value
        ]
        self.unsave_keyboard_bindings = True

    def remove_temp_keyboard_binding(self,
                                     device: str,
                                     key_action: str = "None",
                                     gesture: str = "None"):
        """Remove binding from config by providing either key_action or gesture.
        """

        logger.info(
            f"remove_temp_keyboard_binding for device: {device}, key: {key_action} or gesture {gesture}"
        )

        out_keybindings = {}
        for ges, vals in self.temp_keyboard_bindings.items():
            if gesture == ges:
                continue
            if key_action == vals[1]:
                continue

            out_keybindings[ges] = vals

        self.temp_keyboard_bindings = out_keybindings

        self.unsave_keyboard_bindings = True
        return

    def apply_keyboard_bindings(self):
        logger.info("Applying keyboard bindings")

        self.keyboard_bindings = copy.deepcopy(self.temp_keyboard_bindings)
        self.write_keyboard_bindings_file()
        self.unsave_keyboard_bindings = False

    def write_keyboard_bindings_file(self):
        keyboard_bindings_file = Path(self.current_profile_path,
                                      "keyboard_bindings.json")
        logger.info(f"Writing keyboard bindings file {keyboard_bindings_file}")

        with open(keyboard_bindings_file, 'w') as f:
            out_json = dict(sorted(self.keyboard_bindings.items()))
            json.dump(out_json, f, indent=4, separators=(', ', ': '))

    # ---------------------------------------------------------------------------- #
    def apply_all(self):
        self.apply_config()
        self.apply_mouse_bindings()
        self.apply_keyboard_bindings()

    def destroy(self):
        logger.info("Destroy")
