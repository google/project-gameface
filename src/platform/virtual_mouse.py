from src.platform import PlatformDetection
import numpy as np
import wx
from pynput.mouse import *


class VirtualMouse(PlatformDetection):

    def action(self):
        if self.windows:
            print("Not implemented")

    def destroy(self):
        return

