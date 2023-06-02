class PropertiesMeta(type):

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))


# noinspection PyMethodMayBeStatic
class PropertiesInterface(metaclass=PropertiesMeta):

    def get_tk_root_geometry(self) -> str:
        return '1024x658'

    def get_app_icon(self) -> str:
        return "assets/images/icon.ico"

    def get_frame_menu_height(self) -> int:
        return 360

    def get_frame_menu_width(self) -> int:
        return 320
