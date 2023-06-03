class KeyboardMeta(type):

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))


class KeyboardInterface(metaclass=KeyboardMeta):

    def keyDown(self, button):
        pass

    def keyUp(self, button):
        pass