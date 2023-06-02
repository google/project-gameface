from src.platform import PlatformDetection
from src.platform.generic.generic_properties import GenericProperties
from src.platform.interfaces.properties_interface import PropertiesInterface
from src.platform.linux.linux_properties import LinuxProperties


class PropertiesBuilder(PlatformDetection):

    def __init__(self):
        super().__init__()

    def build(self) -> PropertiesInterface:
        if self.is_linux():
            return LinuxProperties()

        return GenericProperties()


