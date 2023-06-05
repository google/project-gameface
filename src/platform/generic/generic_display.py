from typing import List

from src.platform.interfaces.display_interface import DisplayInterface
import wx


class GenericDisplay(DisplayInterface):

    def __init__(self) -> None:
        super().__init__()
        app = wx.App(False)
        self.num_displays = wx.Display.GetCount()
        for i in range(self.num_displays):
            display = wx.Display(i)
            xStart = 0
            yStart = 0
            x = display.GetGeometry().GetSize().x
            y = display.GetGeometry().GetSize().y
            xEnd = display.GetGeometry().GetSize().x
            yEnd = display.GetGeometry().GetSize().y
            cur_display = {
                "id": i,
                "x": x,
                "y": y,
                "x1": xStart,
                "y1": yStart,
                "x2": xEnd,
                "y2": yEnd,
                "center_x": (xStart + xEnd) // 2,
                "center_y": (yStart + yEnd) // 2
            }
            self.displays.append(cur_display)
        # We no longer need this
        del app

