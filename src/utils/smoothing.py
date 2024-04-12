import numpy as np
import numpy.typing as npt


def calc_smooth_kernel(n: int) -> npt.ArrayLike:
    kernel = np.hamming(n * 2)[:n]
    kernel = kernel / kernel.sum()

    return kernel.reshape(n, 1)


def apply_smoothing(data: npt.ArrayLike, kernel: npt.ArrayLike) -> npt.ArrayLike:
    smooth_n = len(kernel)
    return sum(kernel * data[-smooth_n:])
