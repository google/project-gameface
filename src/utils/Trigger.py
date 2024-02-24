from enum import Enum


class Trigger(Enum):
    DYNAMIC = "dynamic"
    RAPID = "rapid"
    SINGLE = "single"
    HOLD = "hold"
    TOGGLE = "toggle"
