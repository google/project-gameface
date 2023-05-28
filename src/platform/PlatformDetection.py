import sys


class PlatformDetection:
    __platform = None
    __windows = False
    __linux = False
    __darwin = False
    __freebsd = False
    __xorg = False
    __wayland = False

    def __init__(self):
        self.__platform = sys.platform
        self.__windows = (self.__platform == "win32")
        self.__darwin = (self.__platform == "darwin")
        self.__linux = (self.__platform == "linux")
        self.__freebsd = ("freebsd" in self.__platform)
        # Need to detect wayland, X as well.
        # May be able to simplify to just a "unix"
