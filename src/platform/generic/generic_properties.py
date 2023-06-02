from src.platform.interfaces.properties_interface import PropertiesInterface


class GenericProperties(PropertiesInterface):

    def __init__(self) -> None:
        super().__init__()

    def get_tk_root_geometry(self) -> str:
        return super().get_tk_root_geometry()

    def get_app_icon(self) -> str:
        return super().get_app_icon()



