class PropertiesMeta(type):

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))


class PropertiesInterface(metaclass=PropertiesMeta):

    def get_tk_root_geometry(self) -> str:
        return '1024x658'

    def get_app_icon(self) -> str:
        return "assets/images/icon.ico"



