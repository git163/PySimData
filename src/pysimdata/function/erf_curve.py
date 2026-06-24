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

    def plot(self, ax=None, **kwargs):
        """曲线图"""
        import matplotlib.pyplot as plt

        if self._data is None:
            raise ValueError("请先调用 generate()")

        if ax is None:
            _, ax = plt.subplots(figsize=(8, 4))

        y = self._data[0, :]
        x = np.linspace(self._params.get("x_range", (-3, 3))[0],
                       self._params.get("x_range", (-3, 3))[1], len(y))
        ax.plot(x, y)
        ax.set_title("ErfCurve")
        ax.grid(True)
        return ax