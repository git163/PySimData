"""仿真数据生成器基类"""
import json
import logging
import os
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


class BaseGenerator:
    """仿真数据生成器基类"""

    # 配置参数映射: json_key -> (param_name, type)
    CONFIG_KEYS: Dict[str, Tuple[str, type]] = {}

    # type 字符串 -> 生成器类 的自动注册表
    _REGISTRY: Dict[str, type] = {}

    def __init_subclass__(cls, **kwargs):
        """子类定义时自动登记到注册表（键为类名）"""
        super().__init_subclass__(**kwargs)
        BaseGenerator._REGISTRY[cls.__name__] = cls

    @classmethod
    def get_generator_class(cls, type_name: str) -> type:
        """按 type 字符串查注册表，未注册则抛异常"""
        if type_name not in BaseGenerator._REGISTRY:
            available = ", ".join(sorted(BaseGenerator._REGISTRY)) or "(空)"
            raise ValueError(
                f"未注册的生成器类型: {type_name}; 可用类型: {available}"
            )
        return BaseGenerator._REGISTRY[type_name]

    def __init__(
        self,
        func: Optional[Callable[..., np.ndarray]] = None,
        data_source: Optional[Dict[str, Any]] = None,
        **params: Any,
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
        self._data: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # 配置：加载
    # ------------------------------------------------------------------
    @classmethod
    def from_config(cls, config: Union[dict, str]) -> "BaseGenerator":
        """
        从字典或 JSON 文件加载配置并创建生成器

        Args:
            config: 配置字典 或 JSON 文件路径

        Returns:
            生成器实例
        """
        if isinstance(config, str):
            config = cls._load_config_file(config)

        config_type = config.get("type")
        if config_type != cls.__name__:
            raise ValueError(f"配置类型不匹配: 期望 {cls.__name__}, 实际 {config_type}")

        params = config.get("params", {})
        # 分离出不在 CONFIG_KEYS 中的额外参数（不做类型转换，原样透传）
        known = {k: v for k, v in params.items() if k in cls.CONFIG_KEYS}
        extra = {k: v for k, v in params.items() if k not in cls.CONFIG_KEYS}

        converted = cls._convert_params(known)
        converted.update(extra)

        return cls(**converted)

    @classmethod
    def _load_config_file(cls, path: str) -> dict:
        """从 JSON 文件读取配置字典（from_config 的内部步骤）"""
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

    # ------------------------------------------------------------------
    # 配置：导出
    # ------------------------------------------------------------------
    def _build_config(self) -> dict:
        """构造配置骨架并填充 params（tuple/list 统一转为 list）"""
        config = {
            "type": self.__class__.__name__,
            "format": "npy",
            "params": {},
        }

        # 反向映射: param_name -> json_key
        reverse_keys = {v[0]: k for k, v in self.CONFIG_KEYS.items()}

        for param_name, value in self._params.items():
            json_key = reverse_keys.get(param_name, param_name)
            if isinstance(value, (tuple, list)):
                value = list(value)
            config["params"][json_key] = value

        return config

    def to_config(self) -> dict:
        """导出配置为字典"""
        return self._build_config()

    def _write_config_file(self, path: str, with_timestamp: bool = False) -> str:
        """将配置写入 JSON 文件，可选追加时间戳字段，返回实际写入路径"""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        config = self.to_config()
        if with_timestamp:
            config["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.debug("Config saved to %s", path)
        return path

    def save_config(self, path: str) -> str:
        """保存配置到 JSON 文件，返回实际写入路径"""
        return self._write_config_file(path, with_timestamp=False)

    # ------------------------------------------------------------------
    # 数据生成
    # ------------------------------------------------------------------
    def generate(self) -> np.ndarray:
        """生成仿真数据"""
        try:
            if self._data_source is not None:
                self._data = self._load_offline_data()
            else:
                self._data = self._func(**self._params)
            logger.debug(
                "%s generated data with shape %s",
                self.__class__.__name__,
                getattr(self._data, "shape", "N/A"),
            )
        except Exception as exc:
            logger.error("生成数据失败: %s", exc)
            raise
        return self._data

    def _load_offline_data(self) -> np.ndarray:
        """内部方法：加载离线数据并返回数组"""
        if not isinstance(self._data_source, dict):
            raise ValueError("data_source 必须是字典")

        path = self._data_source.get("path")
        if path is None:
            raise ValueError("data_source 中必须包含 'path' 字段")

        custom_loader = self._data_source.get("loader")
        if custom_loader is not None:
            return custom_loader(path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"离线数据文件不存在: {path}")

        ext = os.path.splitext(path)[-1].lower()

        if ext in (".npy", ".npz"):
            return np.load(path)
        if ext == ".csv":
            delimiter = self._data_source.get("delimiter", ",")
            return np.loadtxt(path, delimiter=delimiter)
        if ext in (".png", ".jpg", ".jpeg", ".tif", ".tiff"):
            from PIL import Image

            return np.array(Image.open(path))

        raise ValueError(f"不支持的文件格式: {ext}")

    # ------------------------------------------------------------------
    # 持久化：一次性保存全部产物（数据 + 配置 + 预览图）
    # ------------------------------------------------------------------
    def save_all(
        self,
        output_dir: str,
        name: str = "data",
        timestamped: bool = True,
    ) -> str:
        """
        一次性保存全部产物（数据 + 配置 + 预览图）到指定目录

        Args:
            output_dir: 输出目录 (如 "output/gaussian_grid")
            name: 数据文件名前缀
            timestamped: 是否创建时间戳子目录

        Returns:
            实际保存目录路径
        """
        if timestamped:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(output_dir, ts)
        os.makedirs(output_dir, exist_ok=True)

        self._save_data(output_dir, name)
        self._write_config_file(os.path.join(output_dir, "config.json"), with_timestamp=True)
        self._save_preview(output_dir)

        return output_dir

    def _save_data(self, output_dir: str, name: str) -> None:
        """内部方法：保存数据数组为 .npy"""
        if self._data is None:
            return
        np.save(os.path.join(output_dir, f"{name}.npy"), self._data)
        logger.debug("Data saved to %s/%s.npy", output_dir, name)

    def _save_preview(self, output_dir: str) -> None:
        """内部方法：保存预览图 preview.png（matplotlib 缺失时跳过）"""
        try:
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(6, 5))
            self.plot(ax=ax)
            fig.savefig(os.path.join(output_dir, "preview.png"), dpi=150)
            plt.close(fig)
            logger.debug("Preview saved to %s/preview.png", output_dir)
        except ImportError:
            logger.warning("matplotlib 未安装，跳过图片保存")
        except Exception as exc:
            logger.warning("图片保存失败: %s", exc)

    # ------------------------------------------------------------------
    # 可视化
    # ------------------------------------------------------------------
    def _render(self, ax) -> None:
        """在给定坐标轴上渲染数据：二维用 imshow，一维用 plot"""
        data = self.data  # 复用 property 的 None 检查
        if data.ndim == 2 and data.shape[0] > 1:
            ax.imshow(data, cmap="gray")
            ax.set_title(self.__class__.__name__)
        else:
            y = data[0, :] if data.ndim > 1 else data
            ax.plot(y)
            ax.set_title(self.__class__.__name__)
            ax.grid(True)

    def plot(self, ax=None, **kwargs):
        """可视化，子类可重写"""
        import matplotlib.pyplot as plt

        if self._data is None:
            raise ValueError("请先调用 generate()")

        if ax is None:
            _, ax = plt.subplots(figsize=(6, 5))

        self._render(ax)
        return ax

    def save_preview(self, path: str) -> None:
        """保存预览图到指定路径文件"""
        import matplotlib.pyplot as plt

        if self._data is None:
            raise ValueError("请先调用 generate()")

        fig, ax = plt.subplots(figsize=(6, 5))
        self._render(ax)
        # 二维图额外附带色标
        if self._data.ndim == 2 and self._data.shape[0] > 1:
            fig.colorbar(ax.images[0], ax=ax)

        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)

    # ------------------------------------------------------------------
    # 属性
    # ------------------------------------------------------------------
    @property
    def data(self) -> np.ndarray:
        if self._data is None:
            raise ValueError("请先调用 generate()")
        return self._data

    @property
    def params(self) -> dict:
        """返回参数字典"""
        return self._params.copy()
