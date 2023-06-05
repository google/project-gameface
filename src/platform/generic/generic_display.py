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
            xEnd = display.GetGeometry().GetSize().x
            yEnd = display.GetGeometry().GetSize().y
            cur_display = {
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

    def get_displays(self) -> []:
        return self.displays

    def get_current_display(self, mouse) -> tuple[int, object]:
        return super().get_current_display(mouse)

    def size(self) -> tuple[int, int]:
        return [110, 100]
