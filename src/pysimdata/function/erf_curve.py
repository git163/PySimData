"""误差函数 (erf) 生成器"""
import numpy as np
from scipy.special import erf

from ..base import BaseGenerator


class ErfCurve(BaseGenerator):
    """误差函数 (erf) 生成器"""

    CONFIG_KEYS = {
        "x_range": ("x_range", tuple),
        "num_points": ("num_points", int),
        "amplitude": ("amplitude", float),
        "y_shape": ("y_shape", int),
    }

    def __init__(
        self,
        x_range: tuple[float, float] = (-3, 3),
        num_points: int = 100,
        amplitude: float = 1.0,
        y_shape: int = 100,
        data_source: dict | None = None,
    ):
        def _func(x_range, num_points, amplitude, y_shape):
            x = np.linspace(x_range[0], x_range[1], num_points)
            y = erf(x) * amplitude
            return np.tile(y, (y_shape, 1))

        super().__init__(
            func=_func,
            data_source=data_source,
            x_range=x_range,
            num_points=num_points,
            amplitude=amplitude,
            y_shape=y_shape,
        )