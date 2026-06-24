"""单边指数衰减生成器"""
import numpy as np

from ..base import BaseGenerator


class ExponentialDecay(BaseGenerator):
    """单边指数衰减生成器"""

    CONFIG_KEYS = {
        "shape": ("shape", tuple),
        "tau": ("tau", float),
        "amplitude": ("amplitude", float),
        "direction": ("direction", str),
    }

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
                return np.tile(x.reshape(-1, 1), (1, shape[1]))

        super().__init__(
            func=_func,
            data_source=data_source,
            shape=shape,
            tau=tau,
            amplitude=amplitude,
            direction=direction,
        )