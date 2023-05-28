import sys


class PlatformDetection:
    __platform = None
    __windows = False
    __linux = False
    __darwin = False
    __freebsd12 = False
    __freebsd13 = False
    __freebsd14 = False
    __xorg = False
    __wayland = False

    def __init__(self):
        self.__platform = sys.platform
        if self.__platform == "Windows":
            self.__windows = True
        if self.__platform == "darwin":
            self.__darwin = True
        if self.__platform == "linux":
            self.__linux = True
        if self.__platform == "freebsd12":
            self.__freebsd12 = True
        if self.__platform == "freebsd13":
            self.__freebsd13 = True
        if self.__platform == "freebsd14":
            self.__freebsd14 = True
