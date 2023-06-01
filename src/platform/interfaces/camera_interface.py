class CameraMeta(type):

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))


class CameraInterface(metaclass=CameraMeta):

    def action(self):
        pass

    def destroy(self):
        pass
