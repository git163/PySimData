"""高斯点阵生成器"""
import numpy as np

from ..base import BaseGenerator


class GaussianGrid(BaseGenerator):
    """高斯点阵生成器"""

    CONFIG_KEYS = {
        "shape": ("shape", tuple),
        "mean": ("mean", float),
        "std": ("std", float),
        "num_points": ("num_points", int),
        "seed": ("seed", int),
    }

    def __init__(
        self,
        shape: tuple[int, int] = (256, 256),
        mean: float = 0,
        std: float = 1,
        num_points: int = 10,
        seed: int | None = None,
        data_source: dict | None = None,
    ):
        def _func(shape, mean, std, num_points, seed):
            rng = np.random.default_rng(seed)
            data = rng.normal(mean, std, (*shape, num_points))
            return np.sum(data, axis=-1)

        super().__init__(
            func=_func,
            data_source=data_source,
            shape=shape,
            mean=mean,
            std=std,
            num_points=num_points,
            seed=seed,
        )