# 仿真数据生成器框架设计

- 日期: 2026-06-24
- 作者: tshua
- 状态: 草稿
- 关联: pysimdata 项目初始化

## 背景

需要设计一个仿真数据生成框架，用于生成以下类型的仿真数据或图片：
1. 高斯点阵（Gaussian Grid）
2. 高斯束斑（Gaussian Beam）
3. 自定义函数曲线（Function Curve）
4. 误差函数（erf）
5. 双曲正切（tanh）
6. 双曲余弦（cosh）
7. 单边指数衰减
8. 双边高斯分布
9. ...（可扩展）

要求：
- 可扩展化、模块化
- 不同业务场景隔离
- 参考 sklearn datasets 设计风格

## 目标

- 目标 1：每个场景独立为一个类，参数独立设计
- 目标 2：统一接口 `.generate().plot().save()`
- 目标 3：底层 func 直接抽象为核心生成器
- 目标 4：支持离线数据导入（内部机制）
- 非目标：不支持 CLI，仅 Python API

## 方案

### 架构

```
pysimdata/
├── __init__.py
├── base.py              # 基类 BaseGenerator
├── gaussian/
│   ├── __init__.py
│   ├── grid.py        # 高斯点阵
│   └── beam.py       # 高斯束斑
├── function/
│   ├── __init__.py
│   ├── curve.py     # 基础函数曲线 (sin, cos)
│   ├── special.py   # 特殊函数 (erf, tanh, cosh)
│   └── decay.py    # 衰减函数 (指数, 高斯)
```

### 基类设计 (base.py)

核心设计：底层 func 直接作为生成器，支持离线数据导入。

```python
class BaseGenerator:
    """仿真数据生成器基类"""

    def __init__(
        self,
        func: callable | None = None,
        data_source: dict | None = None,
        **params
    ):
        """
        Args:
            func: 核心生成函数，输入 params，返回 np.ndarray
            data_source: 离线数据源配置 {'type': 'xxx', ...}
            **params: 传递给 func 的参数
        """
        self._func = func
        self._data_source = data_source
        self._params = params
        self._data: np.ndarray | None = None

    def generate(self) -> np.ndarray:
        """生成仿真数据"""
        if self._data_source is not None:
            # 离线数据导入
            self._load_offline_data()
        elif self._func is not None:
            # 实时生成
            self._data = self._func(**self._params)
        else:
            raise ValueError("必须提供 func 或 data_source")
        return self._data

    def _load_offline_data(self) -> None:
        """内部方法：加载离线数据"""
        # data_source 格式: {'path': 'xxx.xxx'} 或 {'path': 'xxx.xxx', 'loader': custom_loader}
        # 支持: .npy, .npz, .csv, .png, .jpg, .jpeg
        # 自定义格式: 传入 loader 函数
        import os
        path = self._data_source.get("path")
        custom_loader = self._data_source.get("loader")

        if custom_loader is not None:
            # 自定义加载器
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
        plt.figure()
        plt.imshow(self._data, **kwargs)
        plt.colorbar()
        plt.show()

    def save(self, path: str, **kwargs) -> None:
        """保存为图片文件"""
        from PIL import Image
        if self._data is None:
            raise ValueError("请先调用 generate()")
        # 归一化到 [0, 255]
        data = np.clip(self._data, 0, 255).astype(np.uint8)
        Image.fromarray(data).save(path, **kwargs)

    @property
    def data(self) -> np.ndarray:
        if self._data is None:
            raise ValueError("请先调用 generate()")
        return self._data
```

### 场景 1：高斯点阵 (gaussian/grid.py)

`func` 定义在类内部，类外不可见。

```python
class GaussianGrid(BaseGenerator):
    """高斯点阵生成器"""

    def __init__(
        self,
        shape: tuple[int, int] = (256, 256),
        mean: float = 0,
        std: float = 1,
        num_points: int = 10,
        seed: int | None = None,
        data_source: dict | None = None,
    ):
        # 底层 func 内部定义，类外不可见
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
```

### 场景 2：高斯束斑 (gaussian/beam.py)

`func` 定义在类内部，类外不可见。

```python
class GaussianBeam(BaseGenerator):
    """高斯束斑生成器"""

    def __init__(
        self,
        shape: tuple[int, int] = (256, 256),
        sigma: float = 5,
        amplitude: float = 255,
        center: tuple[int, int] | None = None,
        data_source: dict | None = None,
    ):
        # 底层 func 内部定义，类外不可见
        def _func(shape, sigma, amplitude, center):
            if center is None:
                center = (shape[0] // 2, shape[1] // 2)
            y, x = np.ogrid[:shape[0], :shape[1]]
            y = y - center[0]
            x = x - center[1]
            dist_sq = y**2 + x**2
            return amplitude * np.exp(-dist_sq / (2 * sigma**2))

        super().__init__(
            func=_func,
            data_source=data_source,
            shape=shape,
            sigma=sigma,
            amplitude=amplitude,
            center=center,
        )
```

### 场景 3：基础函数曲线 (function/curve.py)

`func` 定义在类内部，类外不可见。

```python
class FunctionCurve(BaseGenerator):
    """基础函数曲线生成器 (sin, cos 等)"""

    def __init__(
        self,
        func: callable = np.sin,
        x_range: tuple[float, float] = (0, 2 * np.pi),
        num_points: int = 100,
        amplitude: float = 1.0,
        y_shape: int = 100,
        data_source: dict | None = None,
    ):
        def _func(func, x_range, num_points, amplitude, y_shape):
            x = np.linspace(x_range[0], x_range[1], num_points)
            y = func(x) * amplitude
            return np.tile(y, (y_shape, 1))

        super().__init__(
            func=_func,
            data_source=data_source,
            func_inner=func,
            x_range=x_range,
            num_points=num_points,
            amplitude=amplitude,
            y_shape=y_shape,
        )
```

### 场景 4：误差函数 (function/special.py)

```python
class ErfCurve(BaseGenerator):
    """误差函数 (erf) 生成器"""

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
            from scipy.special import erf
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


class TanhCurve(BaseGenerator):
    """双曲正切 (tanh) 生成器"""

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
            y = np.tanh(x) * amplitude
            return np.tile(y, (y_shape, 1))

        super().__init__(
            func=_func,
            data_source=data_source,
            x_range=x_range,
            num_points=num_points,
            amplitude=amplitude,
            y_shape=y_shape,
        )


class CoshCurve(BaseGenerator):
    """双曲余弦 (cosh) 生成器"""

    def __init__(
        self,
        x_range: tuple[float, float] = (-2, 2),
        num_points: int = 100,
        amplitude: float = 1.0,
        y_shape: int = 100,
        data_source: dict | None = None,
    ):
        def _func(x_range, num_points, amplitude, y_shape):
            x = np.linspace(x_range[0], x_range[1], num_points)
            y = np.cosh(x) * amplitude
            return np.tile(y, (y_shape, 1))

        super().__init__(
            func=_func,
            data_source=data_source,
            x_range=x_range,
            num_points=num_points,
            amplitude=amplitude,
            y_shape=y_shape,
        )
```

### 场景 5：衰减函数 (function/decay.py)

```python
class ExponentialDecay(BaseGenerator):
    """单边指数衰减生成器"""

    def __init__(
        self,
        shape: tuple[int, int] = (256, 256),
        tau: float = 10.0,  # 衰减常数
        amplitude: float = 255.0,
        direction: str = "x",  # "x" 或 "y"
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
            # 双边高斯: exp(-(|y| + |x|) / sigma)
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
```

### 导出 (pysimdata/__init__.py)

```python
from .gaussian.grid import GaussianGrid
from .gaussian.beam import GaussianBeam
from .function.curve import FunctionCurve
from .function.special import ErfCurve, TanhCurve, CoshCurve
from .function.decay import ExponentialDecay, BilateralGaussian

__all__ = [
    "GaussianGrid",
    "GaussianBeam",
    "FunctionCurve",
    "ErfCurve",
    "TanhCurve",
    "CoshCurve",
    "ExponentialDecay",
    "BilateralGaussian",
]
```

## 影响范围

- 新增 `src/pysimdata/base.py` 基类
- 新增 `src/pysimdata/gaussian/` 目录及模块
- 新增 `src/pysimdata/function/` 目录及模块
  - `curve.py`: 基础函数曲线 (sin, cos)
  - `special.py`: 特殊函数 (erf, tanh, cosh)
  - `decay.py`: 衰减函数 (指数, 高斯)
- 无兼容性影响

## 风险与对策

- 风险 1: 基类方法 `plot()` 和 `save()` 假设数据是 2D 图像
  - 对策: 添加方法重写或类型检查

## 实施步骤

- [ ] 1. 创建 `src/pysimdata/base.py` 基类
- [ ] 2. 创建 `src/pysimdata/gaussian/` 模块
- [ ] 3. 实现 `GaussianGrid` 类
- [ ] 4. 实现 `GaussianBeam` 类
- [ ] 5. 创建 `src/pysimdata/function/` 模块
- [ ] 6. 实现 `FunctionCurve` 类
- [ ] 7. 添加更多函数类型（erf, tanh, cosh, 单边指数, 双边高斯等）
- [ ] 8. 更新 `__init__.py` 导出
- [ ] 9. 单元测试

## 测试计划

- 单元测试覆盖每个类的 `generate()` 方法
- 验证数据形状和类型
- 验证 `plot()` 和 `save()` 基本可用