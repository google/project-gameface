# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Right-Left swapped
blendshape_names = [
    "None",
    "Lower right eyebrow",
    "Lower left eyebrow",
    "browInnerUp",
    "Raise right eyebrow",
    "Raise left eyebrow",
    "cheekPuff",
    "cheekSquintRight",
    "cheekSquintLeft",
    "Eye blink right",
    "Eye blink left",
    "eyeLookDownRight",
    "eyeLookDownLeft",
    "eyeLookInRight",
    "eyeLookInLeft",
    "eyeLookOutRight",
    "eyeLookOutLeft",
    "eyeLookUpRight",
    "eyeLookUpLeft",
    "eyeSquintRight",
    "eyeSquintLeft",
    "eyeWideRight",
    "eyeWideLeft",
    "jawForward",
    "jawRight",
    "Open mouth",
    "jawLeft",
    "mouthClose",
    "mouthDimpleRight",
    "mouthDimpleLeft",
    "mouthFrownRight",
    "mouthFrownLeft",
    "mouthFunnel",
    "Mouth right",
    "mouthLowerDownRight",
    "mouthLowerDownLeft",
    "mouthPressRight",
    "mouthPressLeft",
    "mouthPucker",
    "Mouth left",
    "Roll lower mouth",
    "Roll upper mouth",
    "mouthShrugLower",
    "mouthShrugUpper",
    "mouthSmileRight",
    "mouthSmileLeft",
    "mouthStretchRight",
    "mouthStretchLeft",
    "mouthUpperUpRight",
    "mouthUpperUpLeft",
    "noseSneerRight",
    "noseSneerLeft",
]
blendshape_indices = {name: i for i, name in enumerate(blendshape_names)}

available_actions = {
    "Mouse left click": ["mouse", "left"],
    "Mouse right click": ["mouse", "right"],
    "Mouse middle click": ["mouse", "middle"],
    "Mouse pause / unpause": ["meta", "pause"],
    "Reset cursor to center": ["meta", "reset"],
    "Switch focus between monitors": ["meta", "cycle"],
}
available_actions_keys = list(available_actions.keys())
available_actions_values = list(available_actions.values())

available_gestures = {
    name: "assets/images/dropdowns/" + name + ".png"
    for name in (
        "None",
        "Eye blink right",
        "Eye blink left",
        "Open mouth",
        "Mouth left",
        "Mouth right",
        "Roll lower mouth",
        "Raise left eyebrow",
        "Lower left eyebrow",
        "Raise right eyebrow",
        "Lower right eyebrow",
    )
}


for k, v in available_gestures.items():
    assert k in blendshape_names, f"{k} not in blendshape_names"
available_gestures_keys = list(available_gestures.keys())

# Map tkinter character to valid pyautogui character
keyboard_keys = {
    # Numbers
    "0": "0",
    "1": "1",
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    # Functions
    "f1": "f1",
    "f2": "f2",
    "f3": "f3",
    "f4": "f4",
    "f5": "f5",
    "f6": "f6",
    "f7": "f7",
    "f8": "f8",
    "f9": "f9",
    "f10": "f10",
    "f11": "f11",
    "f12": "f12",
    # Letters
    "a": "a",
    "b": "b",
    "c": "c",
    "d": "d",
    "e": "e",
    "f": "f",
    "g": "g",
    "h": "h",
    "i": "i",
    "j": "j",
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "o": "o",
    "p": "p",
    "q": "q",
    "r": "r",
    "s": "s",
    "t": "t",
    "u": "u",
    "v": "v",
    "w": "w",
    "x": "x",
    "y": "y",
    "z": "z",
    # Special characters
    "exclam": "!",
    "at": "@",
    "numbersign": "#",
    "dollar": "$",
    "percent": "%",
    "asciicircum": "^",
    "ampersand": "&",
    "asterisk": "*",
    "parenleft": "(",
    "parenright": ")",
    "minus": "-",
    "plus": "+",
    "underscore": "_",
    "equal": "=",
    "bracketleft": "[",
    "bracketright": "]",
    "braceleft": "{",
    "braceright": "}",
    "backslash": "\\",
    "semicolon": ";",
    "colon": ":",
    "apostrophe": "'",
    "quotedbl": '"',
    "grave": "`",
    "comma": ",",
    "less": "<",
    "greater": ">",
    "question": "?",
    "slash": "/",
    "asciitilde": "~",
    "bar": "|",
    "period": ".",
    # Miscellaneous
    "return": "enter",
    "backspace": "backspace",
    "tab": "tab",
    "space": "space",
    "delete": "delete",
    "home": "home",
    "end": "end",
    "next": "pagedown",
    "prior": "pageup",
    "win_l": "win",
    "caps_lock": "capslock",
    "shift_l": "shiftleft",
    "shift_r": "shiftright",
    "control_l": "ctrlleft",
    "control_r": "ctrlright",
    "alt_l": "altleft",
    "alt_r": "altright",
    "num_lock": "numlock",
    # Directions
    "up": "up",
    "down": "down",
    "left": "left",
    "right": "right",
}
available_keyboard_keys = list(keyboard_keys.keys())
