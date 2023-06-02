from src.platform.interfaces.properties_interface import PropertiesInterface


class LinuxProperties(PropertiesInterface):

    def __init__(self) -> None:
        super().__init__()

    def get_tk_root_geometry(self) -> str:
        return '1440x900'

    def get_app_icon(self) -> str:
        return "@assets/images/icon.xbm"

    def get_frame_menu_width(self) -> int:
        return 380
