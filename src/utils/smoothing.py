# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import numpy.typing as npt


def calc_smooth_kernel(n: int) -> npt.ArrayLike:
    kernel = np.hamming(n * 2)[:n]
    kernel = kernel / kernel.sum()

    return kernel.reshape(n, 1)


def apply_smoothing(data: npt.ArrayLike,
                    kernel: npt.ArrayLike) -> npt.ArrayLike:
    smooth_n = len(kernel)
    return sum(kernel * data[-smooth_n:])
