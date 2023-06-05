class DisplayMeta(type):

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))


class DisplayInterface(metaclass=DisplayMeta):

    def __init__(self):
        self.num_displays = 0
        self.displays = []

    def get_displays(self) -> []:
        return self.displays

    def get_current_display(self, mouse) -> tuple[int, object]:
        x, y = mouse.position()
        for mon_id, mon in enumerate(self.displays):
            if mon["x1"] <= x <= mon["x2"] \
                    and mon["y1"] <= y <= mon["y2"]:
                return [mon_id, mon]
        return 0, None

    def get_current_display_size(self, mouse) -> tuple[int, int]:
        display_id, display = self.get_current_display(mouse)
        return [
            display["x"],
            display["y"]
        ]
