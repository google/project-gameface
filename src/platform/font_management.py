from src.platform.PlatformDetection import PlatformDetection
import ctypes


class FontManagement(PlatformDetection):

    def add_font_resource(self, font_file: str) -> None:
        if self.__windows:
            gdi32 = ctypes.WinDLL('gdi32')
            gdi32.AddFontResourceW(font_file)

    def remove_font_resource(self, font_file: str) -> None:
        if self.__windows:
            gdi32 = ctypes.WinDLL('gdi32')
            gdi32.RemoveFontResourceW(font_file)
