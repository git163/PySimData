"""基础函数曲线生成器"""
import numpy as np

from ..base import BaseGenerator

# 函数名到函数的映射
_FUNC_MAP = {
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "log": np.log,
    "sqrt": np.sqrt,
}


class FunctionCurve(BaseGenerator):
    """基础函数曲线生成器 (sin, cos 等)"""

    CONFIG_KEYS = {
        "x_range": ("x_range", tuple),
        "num_points": ("num_points", int),
        "amplitude": ("amplitude", float),
        "y_shape": ("y_shape", int),
    }

    def __init__(
        self,
        func: callable = np.sin,
        x_range: tuple[float, float] = (0, 2 * np.pi),
        num_points: int = 100,
        amplitude: float = 1.0,
        y_shape: int = 100,
        data_source: dict | None = None,
    ):
        # 保存原始函数
        self._func_original = func

        def _func_wrapper(x_range, num_points, amplitude, y_shape):
            x = np.linspace(x_range[0], x_range[1], num_points)
            y = self._func_original(x) * amplitude
            return np.tile(y, (y_shape, 1))

        super().__init__(
            func=_func_wrapper,
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
        x = np.linspace(self._params.get("x_range", (0, 2*np.pi))[0],
                       self._params.get("x_range", (0, 2*np.pi))[1], len(y))
        ax.plot(x, y)
        ax.set_title("FunctionCurve")
        ax.grid(True)
        return ax

    @classmethod
    def from_config(cls, config: dict | str) -> "FunctionCurve":
        """从配置创建，支持字符串函数名"""
        if isinstance(config, str):
            config = cls.load_config_file(config)

        params = config.get("params", {})

        # 转换 func 字符串到函数
        func = np.sin  # 默认
        if "func" in params:
            func_name = params.pop("func")
            if isinstance(func_name, str):
                func = _FUNC_MAP.get(func_name, np.sin)

        # 类型转换 (不处理 func)
        params = cls._convert_params(params)

        return cls(func=func, **params)

    def to_config(self) -> dict:
        """导出配置为字典"""
        config = {
            "type": self.__class__.__name__,
            "format": "npy",
            "params": {},
        }

        reverse_keys = {v[0]: k for k, v in self.CONFIG_KEYS.items()}

        for param_name, value in self._params.items():
            json_key = reverse_keys.get(param_name, param_name)

            # func 需要特殊处理
            if param_name == "x_range" and isinstance(value, (tuple, list)):
                value = list(value)
            config["params"][json_key] = value

        # 添加 func
        func_name = "sin"
        for name, fn in _FUNC_MAP.items():
            if fn == self._func_original:
                func_name = name
                break
        config["params"]["func"] = func_name

        return config