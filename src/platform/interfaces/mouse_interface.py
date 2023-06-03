class MouseMeta(type):

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))


class MouseInterface(metaclass=MouseMeta):

    def destroy(self):
        pass

    def click(self, button, count=1):
        pass

    def mouseDown(self, button):
        pass

    def mouseUp(self, button):
        pass

    def mouseLeft(self, button):
        pass

    def mouseRight(self, button):
        pass

    def position(self) -> tuple:
        return 0, 0

    def moveTo(self, x: int, y: int) -> tuple:
        pass
