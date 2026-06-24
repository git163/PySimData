# 框架设计与新仿真支持指南

- 日期：2026-06-24
- 作者：tshua
- 状态：正式版
- 关联：[初始设计文档](2026-06-24-simdata-generator-design.md)

---

## 一、框架总览

### 1.1 项目结构

```
pysimdata/
├── src/pysimdata/
│   ├── __init__.py            # 包入口，统一导出
│   ├── base.py                # 基类 BaseGenerator
│   └── function/              # 仿真函数模块（按功能域内聚）
│       ├── __init__.py        # 子模块导出
│       ├── gaussian_grid.py   # 高斯点阵
│       ├── gaussian_beam.py   # 高斯束斑
│       ├── function_curve.py  # 基础函数曲线 (sin/cos/tan/exp/log/sqrt)
│       ├── erf_curve.py       # 误差函数 erf
│       ├── tanh_curve.py      # 双曲正切 tanh
│       ├── cosh_curve.py      # 双曲余弦 cosh
│       ├── exp_decay.py       # 单边指数衰减
│       └── bilateral_gaussian.py  # 双边高斯分布
├── tests/
│   └── pysimdata/
│       ├── test_base.py       # 基类测试
│       ├── test_gaussian.py   # 高斯类测试
│       ├── test_function.py   # 函数曲线类测试
│       └── test_config.py     # 配置加载/保存测试
├── examples/                  # 示例脚本
├── docs/                      # 设计文档
└── pyproject.toml
```

### 1.2 设计理念

框架遵循 **「约定优于配置」** 原则，核心思想：

1. **基层抽象**：`BaseGenerator` 提供统一的生成、可视化、序列化流程
2. **函数注入**：每个子类的核心算法封装为内部闭包 `_func`，对外不可见
3. **配置驱动**：通过 `CONFIG_KEYS` 声明式映射 JSON 配置 ↔ Python 参数，支持配置文件的 round-trip
4. **离线兼容**：除实时生成外，支持从 `.npy`/`.csv`/`.png` 等文件加载数据，保持统一接口

### 1.3 核心类图

```
BaseGenerator                          # 抽象基类
├── CONFIG_KEYS: dict                  # 配置键映射（类属性）
├── __init__(func, data_source, **params)
├── generate() -> np.ndarray           # 生成/加载数据
├── plot(ax) -> Axes                   # 可视化（子类可覆写）
├── save(output_dir, name) -> str      # 保存数据+配置+预览
├── save_config(path)                  # 导出 JSON 配置
├── save_image(path)                   # 导出图片
├── to_config() -> dict                # 导出为配置字典
├── from_config(config) -> Self       # 从配置创建（类方法）
└── data -> np.ndarray                 # 数据属性（只读）
    └── 继承 ───────────────────────────────┐
                                            │
GaussianGrid    GaussianBeam   FunctionCurve   ErfCurve   TanhCurve   ...
```

---

## 二、基类 BaseGenerator 详解

### 2.1 构造函数

```python
class BaseGenerator:
    CONFIG_KEYS: dict = {}   # 子类定义: json_key -> (param_name, python_type)

    def __init__(
        self,
        func: Callable | None = None,      # 核心生成函数（闭包）
        data_source: dict | None = None,    # 离线数据源
        **params: Any,                      # 传递给 func 的参数
    ):
```

**两个生成路径**：
| 路径 | `func` | `data_source` | 说明 |
|------|--------|---------------|------|
| 实时生成 | ✅ 必传 | `None` | `generate()` 调用 `func(**params)` |
| 离线加载 | `None` | ✅ 必传 | `generate()` 从文件加载数据 |

传参方式：
```python
# 方式 A：直接传参（最常用）
gen = GaussianBeam(shape=(256, 256), sigma=10, amplitude=255)

# 方式 B：从配置重建
gen = GaussianBeam.from_config("config.json")

# 方式 C：离线数据导入
gen = GaussianBeam(data_source={"path": "data.npy"})
```

### 2.2 配置系统 (CONFIG_KEYS)

`CONFIG_KEYS` 是连接 Python 代码与 JSON 配置的桥梁，定义在子类上：

```python
class ErfCurve(BaseGenerator):
    CONFIG_KEYS = {
        "x_range":    ("x_range",    tuple),   # JSON key "x_range" → Python 参数 "x_range"，类型 tuple
        "num_points": ("num_points", int),
        "amplitude":  ("amplitude",  float),
        "y_shape":    ("y_shape",    int),
    }
```

映射规则：
- `key` — JSON 中的字段名
- `(param_name, type)` — Python 参数名和期望类型
- 类型支持：`int`, `float`, `str`, `tuple`, `list`, `bool`
- `tuple`/`list` 在 JSON 中以数组 `[1, 2, 3]` 存储，加载时自动转换
- **不在 `CONFIG_KEYS` 中的参数** 原样保留，不做类型转换

配置 round-trip 保证：`gen.to_config() → from_config(config) → 生成相同数据`

### 2.3 数据与可视化流程

```
初始化参数 → generate() → self._data (np.ndarray)
                  ↓
              plot() / save_image()     → 可视化
              save()                    → 保存 .npy + config.json + preview.png
              to_config() / save_config() → 导出配置
```

`plot()` 方法可被子类覆写，默认行为：
- 二维数据 (`ndim == 2`)：`imshow()` 灰度图
- 一维数据：`plot()` 曲线

---

## 三、已有仿真类型一览

| 类名 | 数据维度 | 核心公式 | 关键参数 |
|------|---------|---------|---------|
| `GaussianGrid` | 2D 图像 | 多个随机高斯点阵叠加 | `shape`, `num_points`, `mean`, `std`, `seed` |
| `GaussianBeam` | 2D 图像 | $A \cdot \exp(-(x^2+y^2)/(2\sigma^2))$ | `shape`, `sigma`, `amplitude`, `center` |
| `FunctionCurve` | 2D 图像 | $A \cdot f(x)$ 沿 y 轴平铺 | `func`, `x_range`, `num_points`, `amplitude`, `y_shape` |
| `ErfCurve` | 2D 图像 | $A \cdot \mathrm{erf}(x)$ 平铺 | `x_range`, `num_points`, `amplitude`, `y_shape` |
| `TanhCurve` | 2D 图像 | $A \cdot \tanh(x)$ 平铺 | `x_range`, `num_points`, `amplitude`, `y_shape` |
| `CoshCurve` | 2D 图像 | $A \cdot \cosh(x)$ 平铺 | `x_range`, `num_points`, `amplitude`, `y_shape` |
| `ExponentialDecay` | 2D 图像 | $A \cdot \exp(-x / \tau)$ 平铺 | `shape`, `tau`, `amplitude`, `direction` |
| `BilateralGaussian` | 2D 图像 | $A \cdot \exp(-(|x|+|y|)/\sigma)$ | `shape`, `sigma`, `amplitude`, `center` |

---

## 四、添加新仿真 — 分步指南

以添加 **「正弦波纹 (SineRipple)」** 为例，展示完整流程。

### 第 1 步：创建模块文件

新建 `src/pysimdata/function/sine_ripple.py`：

```python
"""正弦波纹生成器"""
import numpy as np

from ..base import BaseGenerator


class SineRipple(BaseGenerator):
    """正弦波纹生成器 —— 生成径向正弦波纹图案"""

    # ① 声明配置键映射
    CONFIG_KEYS = {
        "shape":       ("shape",       tuple),
        "frequency":   ("frequency",   float),
        "amplitude":   ("amplitude",   float),
        "center":      ("center",      tuple),
        "phase":       ("phase",       float),
    }

    def __init__(
        self,
        shape: tuple[int, int] = (256, 256),
        frequency: float = 0.1,
        amplitude: float = 255.0,
        center: tuple[int, int] | None = None,
        phase: float = 0.0,
        data_source: dict | None = None,
    ):
        # ② 定义核心生成函数（闭包，对外不可见）
        def _func(shape, frequency, amplitude, center, phase):
            if center is None:
                center = (shape[0] // 2, shape[1] // 2)
            y, x = np.ogrid[:shape[0], :shape[1]]
            y = y - center[0]
            x = x - center[1]
            r = np.sqrt(y**2 + x**2)               # 到中心的距离
            return amplitude * np.sin(frequency * r + phase)

        # ③ 调用基类 __init__
        super().__init__(
            func=_func,
            data_source=data_source,
            shape=shape,
            frequency=frequency,
            amplitude=amplitude,
            center=center,
            phase=phase,
        )

    # ④ （可选）覆写 plot() 自定义可视化
    def plot(self, ax=None, **kwargs):
        """热力图 + 等高线"""
        import matplotlib.pyplot as plt

        if self._data is None:
            raise ValueError("请先调用 generate()")

        if ax is None:
            _, ax = plt.subplots(figsize=(6, 5))

        ax.imshow(self._data, cmap="RdBu", **kwargs)
        ax.set_title("SineRipple")
        return ax
```

### 第 2 步：注册导出

在 `src/pysimdata/function/__init__.py` 中添加：

```python
from .sine_ripple import SineRipple

__all__ = [
    # ... 已有导出 ...
    "SineRipple",      # ← 新增
]
```

在 `src/pysimdata/__init__.py` 中同步添加导入和 `__all__`。

### 第 3 步：编写示例

新建 `examples/09_sine_ripple.py`：

```python
"""SineRipple: 正弦波纹"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import SineRipple

gen = SineRipple(shape=(256, 256), frequency=0.05, amplitude=128)
data = gen.generate()
print(f"SineRipple: shape={data.shape}, min={data.min():.1f}, max={data.max():.1f}")
gen.save("output/sine_ripple")
```

### 第 4 步：编写单元测试

新建 `tests/pysimdata/test_sine_ripple.py`：

```python
"""SineRipple 测试"""
import json, os, tempfile
import numpy as np
import pytest
from pysimdata.function import SineRipple


class TestSineRipple:
    """SineRipple 单元测试"""

    def test_default_generate(self):
        """默认参数生成"""
        gen = SineRipple()
        data = gen.generate()
        assert data.shape == (256, 256)
        assert data.dtype == np.float64

    def test_custom_params(self):
        """自定义参数"""
        gen = SineRipple(shape=(128, 128), frequency=0.2, amplitude=100, phase=np.pi/2)
        data = gen.generate()
        assert data.shape == (128, 128)

    def test_data_property(self):
        """data 属性"""
        gen = SineRipple()
        gen.generate()
        assert gen.data.shape == (256, 256)

    def test_data_before_generate(self):
        """generate 前访问 data 应抛异常"""
        gen = SineRipple()
        with pytest.raises(ValueError, match="请先调用 generate"):
            _ = gen.data

    def test_from_config_dict(self):
        """从字典加载配置"""
        config = {
            "type": "SineRipple",
            "params": {"shape": [64, 64], "frequency": 0.1, "amplitude": 200},
        }
        gen = SineRipple.from_config(config)
        data = gen.generate()
        assert data.shape == (64, 64)

    def test_to_config(self):
        """导出配置"""
        gen = SineRipple(shape=(128, 128), frequency=0.1, amplitude=255, phase=0.0)
        config = gen.to_config()
        assert config["type"] == "SineRipple"
        assert config["params"]["shape"] == [128, 128]
        assert config["params"]["frequency"] == 0.1

    def test_roundtrip(self):
        """创建 → 导出 → 导入 → 生成，数据一致"""
        gen1 = SineRipple(shape=(64, 64), frequency=0.1, amplitude=200, phase=0.5)
        data1 = gen1.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            gen1.save_config(config_path)
            gen2 = SineRipple.from_config(config_path)
            data2 = gen2.generate()

        np.testing.assert_array_almost_equal(data1, data2)

    def test_offline_data(self):
        """离线数据加载"""
        gen1 = SineRipple(shape=(32, 32))
        data1 = gen1.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            npy_path = os.path.join(tmpdir, "data.npy")
            np.save(npy_path, data1)

            gen2 = SineRipple(data_source={"path": npy_path})
            data2 = gen2.generate()
            np.testing.assert_array_almost_equal(data1, data2)
```

### 第 5 步：验证

```bash
# 运行新示例
python examples/09_sine_ripple.py

# 运行全部测试
pytest tests/pysimdata/test_sine_ripple.py -v

# lint 检查
ruff check src/pysimdata/function/sine_ripple.py
```

---

## 五、新仿真开发的检查清单

开发一个新仿真类型时，按以下清单逐项确认：

| # | 检查项 | 说明 |
|---|--------|------|
| 1 | **数学公式明确** | 核心公式表述清晰，参数语义明确 |
| 2 | **CONFIG_KEYS 完整** | 所有需要序列化的参数均在 `CONFIG_KEYS` 中声明，含正确的 Python 类型 |
| 3 | **构造函数签名正确** | 参数有类型注解和默认值，`data_source` 参数保留 |
| 4 | **闭包 _func 纯净** | 不依赖外部可变状态，仅使用传入的参数，可被 pickle |
| 5 | **基类 __init__ 正确调用** | 向 `super().__init__()` 传入 `func`、`data_source` 和所有参数 |
| 6 | **plot() 按需覆写** | 默认的 imshow/plot 不适用时，覆写 `plot()` 提供领域可视化 |
| 7 | **__init__.py 导出** | 在 `function/__init__.py` 和顶级 `__init__.py` 中注册 |
| 8 | **示例脚本** | 新建 `examples/` 下的示例文件，演示基本用法 |
| 9 | **单元测试** | 必须覆盖：默认生成、自定义参数、data 属性、from_config、to_config、roundtrip、离线加载 |
| 10 | **参数经验建议** | 在类 docstring 中给出参数的经验取值范围 |

---

## 六、常见仿真类型设计模板

### 6.1 曲线平铺型（类似 ErfCurve / TanhCurve）

适用于：一维函数 $y = f(x)$ 沿 y 轴重复平铺为 2D 图像。

**参数模板**：`x_range` (tuple), `num_points` (int), `amplitude` (float), `y_shape` (int)

```python
def _func(x_range, num_points, amplitude, y_shape):
    x = np.linspace(x_range[0], x_range[1], num_points)
    y = YOUR_FUNCTION(x) * amplitude
    return np.tile(y, (y_shape, 1))
```

### 6.2 中心扩散型（类似 GaussianBeam / BilateralGaussian）

适用于：从中心向四周呈某种衰减分布的 2D 图案。

**参数模板**：`shape` (tuple), `sigma` (float), `amplitude` (float), `center` (tuple|None)

```python
def _func(shape, sigma, amplitude, center):
    if center is None:
        center = (shape[0] // 2, shape[1] // 2)
    y, x = np.ogrid[:shape[0], :shape[1]]
    y, x = y - center[0], x - center[1]
    r = np.sqrt(y**2 + x**2)            # 欧氏距离
    # r = np.abs(y) + np.abs(x)         # 曼哈顿距离（双边）
    return amplitude * YOUR_DECAY(r, sigma)
```

### 6.3 方向性衰减型（类似 ExponentialDecay）

适用于：沿某个方向（x 或 y）衰减的模式。

**参数模板**：`shape` (tuple), `tau` (float), `amplitude` (float), `direction` (str)

```python
def _func(shape, tau, amplitude, direction):
    if direction == "x":
        x = np.arange(shape[1])
        y = amplitude * YOUR_DECAY(x, tau)
        return np.tile(y, (shape[0], 1))
    else:
        y = np.arange(shape[0])
        x = amplitude * YOUR_DECAY(y, tau)
        return np.tile(x[:, None], (1, shape[1]))
```

### 6.4 随机噪声型（类似 GaussianGrid）

适用于：带随机种子的多粒子/噪声叠加图案。

**参数模板**：`shape` (tuple), `seed` (int|None)，以及其他领域参数

```python
def _func(shape, ..., seed):
    rng = np.random.default_rng(seed)
    data = np.zeros(shape, dtype=np.float64)
    # ... 使用 rng 生成随机分布 ...
    return data
```

### 6.5 参数化函数曲线型（类似 FunctionCurve）

适用于：用户可传入任意 `callable` 的场景。

**要点**：需要覆写 `from_config()` 和 `to_config()`，支持函数名 ↔ 字符串映射。

```python
_FUNC_MAP = {"sin": np.sin, "cos": np.cos}

class MyFunctionCurve(BaseGenerator):
    def __init__(self, func: callable = np.sin, ...):
        self._func_original = func   # 保存原始函数引用
        def _wrapper(...):
            return self._func_original(x) * amp
        super().__init__(func=_wrapper, ...)

    @classmethod
    def from_config(cls, config):
        # 将字符串 func 名转为 callable
        ...

    def to_config(self):
        # 将 callable 转为字符串
        ...
```

---

## 七、架构决策记录 (ADR)

| 决策 | 选择 | 理由 |
|------|------|------|
| 生成函数放在哪儿 | 构造函数内的闭包 | 类外不可见，避免接口污染；参数通过闭包捕获 |
| 模块组织方式 | 按功能域分子目录 | 初期简单，后续可按 `spatial/`, `decay/`, `noise/` 等细分 |
| 配置格式 | JSON | 人类可读可写，易于跨语言交换 |
| 可视化工具 | matplotlib | Python 生态标准，支持静态图和交互式 Jupyter |
| 数据格式 | `.npy` | NumPy 原生，零解析开销，支持内存映射 |
| Python 版本 | ≥ 3.9 | 兼顾 `tuple[int, int]` 等新式类型注解 |
| 测试框架 | pytest | 社区标准，fixture 强大 |

---

## 八、后续扩展方向

1. **3D 数据支持**：当前所有仿真输出 2D `ndarray`，可扩展出 `BaseGenerator3D` 支持体积数据
2. **参数校验**：可增加 `_validate_params()` 钩子，在构造函数中自动校验参数合法范围
3. **生成管道**：支持多个生成器的链式组合（叠加、混叠、mask 等），类似 `sklearn.pipeline`
4. **性能优化**：对大尺寸数据，`_func` 内部可用 `numba.jit` 加速，基类不感知
5. **更多仿真类型**：泊松噪声、Perlin 噪声、Voronoi 图案、衍射光斑、散斑图案等
