"""衰减函数生成器"""
import numpy as np

from ..base import BaseGenerator


class ExponentialDecay(BaseGenerator):
    """单边指数衰减生成器"""

    def __init__(
        self,
        shape: tuple[int, int] = (256, 256),
        tau: float = 10.0,
        amplitude: float = 255.0,
        direction: str = "x",
        data_source: dict | None = None,
    ):
        def _func(shape, tau, amplitude, direction):
            if direction == "x":
                x = np.arange(shape[1])
                y = amplitude * np.exp(-x / tau)
                return np.tile(y, (shape[0], 1))
            else:
                y = np.arange(shape[0])
                x = amplitude * np.exp(-y / tau)
                return np.tile(x, (1, shape[1]))

        super().__init__(
            func=_func,
            data_source=data_source,
            shape=shape,
            tau=tau,
            amplitude=amplitude,
            direction=direction,
        )


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