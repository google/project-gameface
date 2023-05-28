import sys
import wx
import numpy as np
from pynput.keyboard import *
from pynput.mouse import *
from src.platform import PlatformDetection


class HardwareManagement(PlatformDetection):

    def get_displays(self):
        if self.windows:
            print("Not implemented")

    def get_current_display(self):
        if self.windows:
            print("Not implemented")

