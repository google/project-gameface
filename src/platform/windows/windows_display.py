import sys

from src.platform.interfaces.display_interface import DisplayInterface

if sys.platform == "win32":
    import win32api


class WindowsDisplay(DisplayInterface):

    def __init__(self) -> DisplayInterface:
        monitors = win32api.EnumDisplayMonitors()
        self.num_displays = len(enumerate(monitors))
        for i, (_, _, loc) in enumerate(monitors):
            cur_display = {
                "id": i,
                "x": loc[2],
                "y": loc[3],
                "x1": loc[0],
                "y1": loc[1],
                "x2": loc[2],
                "y2": loc[3],
                "center_x": (loc[0] + loc[2]) // 2,
                "center_y": (loc[1] + loc[3]) // 2
            }
            self.displays.append(cur_display)




