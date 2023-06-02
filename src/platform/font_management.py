from src.platform.detection.platform_detection import PlatformDetection
from src.platform.generic.generic_font import GenericFont
from src.platform.windows.windows_font import WindowsFont


class FontManagement(PlatformDetection):

    def __init__(self):
        super().__init__()
        if self.is_windows():
            self.manager = WindowsFont()
        else:
            self.manager = GenericFont()

    def add_font_resource(self, font_file: str) -> None:
        self.manager.add_font_resource(font_file)

    def remove_font_resource(self, font_file: str) -> None:
        self.manager.remove_font_resource(font_file)
