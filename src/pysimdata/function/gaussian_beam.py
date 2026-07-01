"""高斯束斑生成器"""
from typing import Optional, Tuple

import numpy as np

from ..base import BaseGenerator


class GaussianBeam(BaseGenerator):
    """高斯束斑生成器"""

    CONFIG_KEYS = {
        "shape": ("shape", tuple),
        "sigma": ("sigma", float),
        "amplitude": ("amplitude", float),
        "center": ("center", tuple),
    }

    def __init__(
        self,
        shape: Tuple[int, int] = (256, 256),
        sigma: float = 5,
        amplitude: float = 255,
        center: Optional[Tuple[int, int]] = None,
        data_source: Optional[dict] = None,
    ):
        def _func(shape, sigma, amplitude, center):
            if center is None:
                center = (shape[0] // 2, shape[1] // 2)
            y, x = np.ogrid[: shape[0], : shape[1]]
            y = y - center[0]
            x = x - center[1]
            dist_sq = y**2 + x**2
            return amplitude * np.exp(-dist_sq / (2 * sigma**2))

        super().__init__(
            func=_func,
            data_source=data_source,
            shape=shape,
            sigma=sigma,
            amplitude=amplitude,
            center=center,
        )

    def plot(self, ax=None, **kwargs):
        """热力图"""
        import matplotlib.pyplot as plt

        if self._data is None:
            raise ValueError("请先调用 generate()")

        if ax is None:
            _, ax = plt.subplots(figsize=(6, 5))

        ax.imshow(self._data, cmap="hot")
        ax.set_title("GaussianBeam")
        return ax