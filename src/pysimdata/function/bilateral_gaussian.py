"""双边高斯分布生成器"""
import numpy as np

from ..base import BaseGenerator


class BilateralGaussian(BaseGenerator):
    """双边高斯分布生成器"""

    def __init__(
        self,
        shape: tuple[int, int] = (256, 256),
        sigma: float = 10.0,
        amplitude: float = 255.0,
        center: tuple[int, int] | None = None,
        data_source: dict | None = None,
    ):
        def _func(shape, sigma, amplitude, center):
            if center is None:
                center = (shape[0] // 2, shape[1] // 2)
            y, x = np.ogrid[:shape[0], :shape[1]]
            y = y - center[0]
            x = x - center[1]
            dist = np.abs(y) + np.abs(x)
            return amplitude * np.exp(-dist / sigma)

        super().__init__(
            func=_func,
            data_source=data_source,
            shape=shape,
            sigma=sigma,
            amplitude=amplitude,
            center=center,
        )