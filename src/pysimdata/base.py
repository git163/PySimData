"""仿真数据生成器基类"""
import os
from typing import Any, Callable

import numpy as np


class BaseGenerator:
    """仿真数据生成器基类"""

    def __init__(
        self,
        func: Callable | None = None,
        data_source: dict | None = None,
        **params: Any
    ):
        """
        Args:
            func: 核心生成函数，输入 params，返回 np.ndarray
            data_source: 离线数据源配置 {'path': 'xxx.xxx', ...}
            **params: 传递给 func 的参数
        """
        if func is None and data_source is None:
            raise ValueError("必须提供 func 或 data_source")
        self._func = func
        self._data_source = data_source
        self._params = params
        self._data: np.ndarray | None = None

    def generate(self) -> np.ndarray:
        """生成仿真数据"""
        if self._data_source is not None:
            self._load_offline_data()
        else:
            self._data = self._func(**self._params)
        return self._data

    def _load_offline_data(self) -> None:
        """内部方法：加载离线数据"""
        path = self._data_source.get("path")
        custom_loader = self._data_source.get("loader")

        if custom_loader is not None:
            self._data = custom_loader(path)
            return

        ext = os.path.splitext(path)[-1].lower()

        if ext in (".npy", ".npz"):
            self._data = np.load(path)
        elif ext == ".csv":
            delimiter = self._data_source.get("delimiter", ",")
            self._data = np.loadtxt(path, delimiter=delimiter)
        elif ext in (".png", ".jpg", ".jpeg", ".tif", ".tiff"):
            from PIL import Image
            self._data = np.array(Image.open(path))
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    def plot(self, **kwargs) -> None:
        """可视化（matplotlib）"""
        import matplotlib.pyplot as plt
        if self._data is None:
            raise ValueError("请先调用 generate()")
        plt.figure()
        plt.imshow(self._data, **kwargs)
        plt.colorbar()
        plt.show()

    def save(self, path: str, **kwargs) -> None:
        """保存为图片文件"""
        from PIL import Image
        if self._data is None:
            raise ValueError("请先调用 generate()")
        data = np.clip(self._data, 0, 255).astype(np.uint8)
        Image.fromarray(data).save(path, **kwargs)

    @property
    def data(self) -> np.ndarray:
        if self._data is None:
            raise ValueError("请先调用 generate()")
        return self._data