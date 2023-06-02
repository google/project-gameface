class FontMeta(type):

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))


class FontInterface(metaclass=FontMeta):

    def __init__(self) -> None:
        pass

    def add_font_resource(self, font_file: str) -> None:
        pass

    def remove_font_resource(self, font_file: str) -> None:
        pass
