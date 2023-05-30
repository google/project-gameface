class DisplayMeta(type):

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))


class DisplayInterface(metaclass=DisplayMeta):

    def __init__(self, class_name, args, instance):
        print("")

    def size(self) -> tuple[int, int]:
        pass

    def get_displays(self):
        pass

    def get_current_display(self):
        pass
