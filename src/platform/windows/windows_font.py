from src.platform.interfaces.font_interface import FontInterface
import ctypes


class WindowsFont(FontInterface):

    def __init__(self) -> None:
        super().__init__()

    def add_font_resource(self, font_file: str) -> None:
        if self.is_windows():
            gdi32 = ctypes.WinDLL('gdi32')
            gdi32.AddFontResourceW(font_file)

    def remove_font_resource(self, font_file: str) -> None:
        if self.is_windows():
            gdi32 = ctypes.WinDLL('gdi32')
            gdi32.RemoveFontResourceW(font_file)
