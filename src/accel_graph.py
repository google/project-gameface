import abc
import math


class AccelGraph(metaclass=abc.ABCMeta):

    def __init__(self):
        pass

    @abc.abstractmethod
    def __call__(self, x: float) -> float:
        pass


class SigmoidAccel(AccelGraph):

    def __init__(self, shift_x=5, slope=0.3, multiply=1.2):
        super().__init__()
        self.shift_x = shift_x
        self.slope = slope
        self.multiply = multiply

    def __call__(self, x: float) -> float:
        x = abs(x)
        sig = 1 / (1 + math.exp(-self.slope * (x - self.shift_x)))
        return self.multiply * sig
