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
            # 生成 n*n 个小束斑组成的点阵
            grid_size = int(np.sqrt(num_points))
            if grid_size * grid_size != num_points:
                grid_size = int(np.ceil(np.sqrt(num_points)))

            cell_h = shape[0] // grid_size
            cell_w = shape[1] // grid_size

            rng = np.random.default_rng(seed)
            result = np.zeros(shape, dtype=np.float64)

            for i in range(grid_size):
                for j in range(grid_size):
                    if i * grid_size + j >= num_points:
                        break
                    # 每个位置的随机参数
                    amp = rng.normal(mean, std)
                    sigma = rng.uniform(2, 5)

                    # 束斑中心
                    cy = i * cell_h + cell_h // 2
                    cx = j * cell_w + cell_w // 2

                    # 生成小束斑
                    y, x = np.ogrid[:shape[0], :shape[1]]
                    y = y - cy
                    x = x - cx
                    dist_sq = y**2 + x**2
                    spot = amp * np.exp(-dist_sq / (2 * sigma**2))

                    # 限制在 cell 区域内
                    y1 = i * cell_h
                    y2 = min((i + 1) * cell_h, shape[0])
                    x1 = j * cell_w
                    x2 = min((j + 1) * cell_w, shape[1])
                    result[y1:y2, x1:x2] += spot[y1:y2, x1:x2]

            return result

        super().__init__(
            func=_func,
            data_source=data_source,
            shape=shape,
            mean=mean,
            std=std,
            num_points=num_points,
            seed=seed,
        )