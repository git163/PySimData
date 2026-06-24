"""仿真数据生成器基类"""
import json
import os
from datetime import datetime
from typing import Any, Callable

import numpy as np


class BaseGenerator:
    """仿真数据生成器基类"""

    # 配置参数映射: json_key -> (param_name, type)
    CONFIG_KEYS: dict = {}

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
        self._config: dict | None = None  # 原始配置

    @classmethod
    def from_config(cls, config: dict | str) -> "BaseGenerator":
        """
        从字典或 JSON 文件加载配置并创建生成器

        Args:
            config: 配置字典 或 JSON 文件路径

        Returns:
            生成器实例
        """
        if isinstance(config, str):
            # 文件路径
            config = cls.load_config_file(config)

        config_type = config.get("type")
        if config_type != cls.__name__:
            raise ValueError(f"配置类型不匹配: 期望 {cls.__name__}, 实际 {config_type}")

        params = config.get("params", {})
        # 保留不在 CONFIG_KEYS 中的参数
        extra_params = {}
        for key in list(params.keys()):
            if key not in cls.CONFIG_KEYS:
                extra_params[key] = params.pop(key)

        # 类型转换
        params = cls._convert_params(params)

        # 合并额外参数
        params.update(extra_params)

        return cls(**params)

    @classmethod
    def load_config_file(cls, path: str) -> dict:
        """从 JSON 文件加载配置"""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def _convert_params(cls, params: dict) -> dict:
        """根据 CONFIG_KEYS 转换参数类型"""
        converted = {}
        for key, value in params.items():
            if value is None:
                converted[key] = None
                continue
            if key in cls.CONFIG_KEYS:
                param_name, param_type = cls.CONFIG_KEYS[key]
                if param_type in (tuple, list) and isinstance(value, list):
                    converted[param_name] = tuple(value) if param_type == tuple else value
                else:
                    converted[param_name] = param_type(value)
            else:
                converted[key] = value
        return converted

    def to_config(self) -> dict:
        """导出配置为字典"""
        config = {
            "type": self.__class__.__name__,
            "format": "npy",
            "params": {},
        }

        # 反向映射: param_name -> json_key
        reverse_keys = {v[0]: k for k, v in self.CONFIG_KEYS.items()}

        for param_name, value in self._params.items():
            json_key = reverse_keys.get(param_name, param_name)
            # tuple/list 转换
            if isinstance(value, (tuple, list)):
                value = list(value)
            config["params"][json_key] = value

        return config

    def save_config(self, path: str) -> None:
        """保存配置到 JSON 文件"""
        config = self.to_config()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

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

    @property
    def params(self) -> dict:
        """返回参数字典"""
        return self._params.copy()