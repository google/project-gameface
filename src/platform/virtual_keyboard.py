from src.platform import PlatformDetection


class VirtualMouse(PlatformDetection):

    def action(self):
        if self.windows:
            print("Not implemented")

    def destroy(self):
        return

