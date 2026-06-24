# 新仿真器接入指南

- 日期：2026-06-24
- 作者：tshua
- 用途：快速参考——按步骤接入一个新的仿真数据类型
- 前置阅读：[框架设计文档](2026-06-24-framework-design-and-new-simulation.md)

---

## 0. 前提：你需要提供什么

在动手写代码之前，先明确两样东西：

| 要素 | 示例 |
|------|------|
| **核心公式** | $z = A \cdot \sin(\omega \cdot r + \phi)$ |
| **参数列表** | `shape`, `frequency`, `amplitude`, `center`, `phase` |

有了这两样，就可以套用下面的模板。

---

## 1. 新建模块文件

在 `src/pysimdata/function/` 下新建一个 `.py` 文件，命名用 `snake_case`，例如 `sine_ripple.py`。

### 1.1 标准模板

```python
"""<仿真名称>生成器 —— 一句话描述"""
import numpy as np

from ..base import BaseGenerator


class <ClassName>(BaseGenerator):
    """<仿真名称>生成器

    公式/原理: <一句话公式>

    参数建议:
        - param_a: <经验取值范围>
        - param_b: <经验取值范围>
    """

    # ── 配置键映射 ─────────────────────────────────
    # 格式: JSON字段名 -> (Python参数名, Python类型)
    CONFIG_KEYS = {
        "shape":     ("shape",     tuple),
        "amplitude": ("amplitude", float),
        # ... 其他需要序列化的参数
    }

    def __init__(
        self,
        shape: tuple[int, int] = (256, 256),
        amplitude: float = 255.0,
        # ... 其他参数（带类型注解和默认值）
        data_source: dict | None = None,      # ← 必须保留
    ):
        # ── 核心生成函数（闭包，对外不可见） ──────
        def _func(shape, amplitude, ...):
            # TODO: 用 numpy 矢量运算实现核心公式
            result = np.zeros(shape, dtype=np.float64)
            # ...
            return result

        # ── 调用基类构造函数 ──────────────────────
        super().__init__(
            func=_func,
            data_source=data_source,
            shape=shape,
            amplitude=amplitude,
            # ... 所有参数逐字传入
        )

    # ── （可选）自定义可视化 ──────────────────────
    def plot(self, ax=None, **kwargs):
        """自定义 plot —— 不覆写则使用基类默认的 imshow/plot"""
        import matplotlib.pyplot as plt

        if self._data is None:
            raise ValueError("请先调用 generate()")

        if ax is None:
            _, ax = plt.subplots(figsize=(6, 5))

        ax.imshow(self._data, cmap="viridis", **kwargs)
        ax.set_title(self.__class__.__name__)
        return ax
```

### 1.2 三种常见 _func 模式

**模式 A：曲线平铺型**（沿 y 轴重复一维函数 → 2D）

```python
def _func(x_range, num_points, amplitude, y_shape):
    x = np.linspace(x_range[0], x_range[1], num_points)
    y = YOUR_FUNC(x) * amplitude
    return np.tile(y, (y_shape, 1))
```

**模式 B：中心扩散型**（从中心点向四周径向衰减/变化）

```python
def _func(shape, sigma, amplitude, center):
    if center is None:
        center = (shape[0] // 2, shape[1] // 2)
    y, x = np.ogrid[:shape[0], :shape[1]]
    y, x = y - center[0], x - center[1]
    r = np.sqrt(y**2 + x**2)          # 欧氏距离
    return amplitude * np.exp(-r / sigma)
```

**模式 C：随机叠加型**（需要 seed 参数控制可复现性）

```python
def _func(shape, ..., seed):
    rng = np.random.default_rng(seed)
    result = np.zeros(shape, dtype=np.float64)
    # ... 用 rng 而非 np.random 以保证可复现
    return result
```

---

## 2. 注册导出

### 2.1 `src/pysimdata/function/__init__.py`

```python
from .<your_file> import <ClassName>   # ← 新增

__all__ = [
    # ... 已有 ...
    "<ClassName>",                       # ← 新增
]
```

### 2.2 `src/pysimdata/__init__.py`

同步添加导入行和 `__all__` 条目。

---

## 3. 编写示例

新建 `examples/<序号>_<name>.py`：

```python
"""<ClassName>: <简短描述>"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import <ClassName>

gen = <ClassName>(<参数>=<值>, ...)
data = gen.generate()
print(f"<ClassName>: shape={data.shape}, min={data.min():.2f}, max={data.max():.2f}")
gen.save("output/<output_subdir>")
```

验证：

```bash
python examples/<序号>_<name>.py
```

---

## 4. 编写测试

新建 `tests/pysimdata/test_<name>.py`，必须覆盖以下用例：

```python
import json, os, tempfile
import numpy as np
import pytest
from pysimdata.function import <ClassName>


class Test<ClassName>:

    # ── 基础功能 ────────────────────
    def test_default_generate(self):
        """默认参数生成结果 shape 正确"""
        gen = <ClassName>()
        data = gen.generate()
        assert data.shape == (256, 256)         # 按默认值调整
        assert data.dtype == np.float64

    def test_custom_params(self):
        """自定义参数，验证 shape 和边界值"""
        gen = <ClassName>(<参数>=<值>, ...)
        data = gen.generate()
        assert data.shape == (<预期的shape>)
        # 如有可验证的边界断言在此添加

    def test_data_property(self):
        """data 属性返回已生成数据"""
        gen = <ClassName>()
        gen.generate()
        assert gen.data is not None

    def test_data_before_generate(self):
        """生成前访问 data 应抛异常"""
        gen = <ClassName>()
        with pytest.raises(ValueError, match="请先调用 generate"):
            _ = gen.data

    # ── 配置序列化 ──────────────────
    def test_from_config_dict(self):
        """从字典加载配置"""
        config = {"type": "<ClassName>", "params": {<参数键值对>}}
        gen = <ClassName>.from_config(config)
        data = gen.generate()
        assert data.shape == (<预期的shape>)

    def test_to_config(self):
        """导出配置，验证 type 和关键字段"""
        gen = <ClassName>(<参数>=<值>, ...)
        config = gen.to_config()
        assert config["type"] == "<ClassName>"
        assert config["params"]["<某个键>"] == <预期值>

    def test_roundtrip(self):
        """创建 → 导出 → 导入 → 生成，数据完全相同"""
        gen1 = <ClassName>(<参数>=<值>, ...)
        data1 = gen1.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            gen1.save_config(config_path)
            gen2 = <ClassName>.from_config(config_path)
            data2 = gen2.generate()

        np.testing.assert_array_almost_equal(data1, data2)

    # ── 离线数据加载 ────────────────
    def test_offline_data(self):
        """从 .npy 文件加载数据"""
        gen1 = <ClassName>(shape=(32, 32))
        data1 = gen1.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            npy_path = os.path.join(tmpdir, "data.npy")
            np.save(npy_path, data1)

            gen2 = <ClassName>(data_source={"path": npy_path})
            data2 = gen2.generate()
            np.testing.assert_array_almost_equal(data1, data2)

    # ── plot（如覆写了则加）─────────
    def test_plot(self):
        """plot() 不抛异常"""
        import matplotlib
        matplotlib.use("Agg")                  # 无 GUI 后端
        import matplotlib.pyplot as plt

        gen = <ClassName>()
        gen.generate()
        fig, ax = plt.subplots()
        result = gen.plot(ax=ax)
        assert result is not None
        plt.close()
```

运行：

```bash
pytest tests/pysimdata/test_<name>.py -v
```

---

## 5. 检查清单

每接入一个新仿真器，逐项勾对：

| ✅ | 检查项 | 说明 |
|----|--------|------|
| ☐ | 公式明确 | 数学公式无误，参数语义清晰 |
| ☐ | CONFIG_KEYS 完整 | 所有需持久化的参数均已映射，类型正确 |
| ☐ | 类型注解 | 构造函数所有参数有类型注解 + 默认值 |
| ☐ | data_source 保留 | 构造函数必须保留 `data_source: dict \| None = None` |
| ☐ | _func 是闭包 | 不依赖外部可变状态，不访问 `self` |
| ☐ | super().__init__ 参数全传 | `func` + `data_source` + 所有参数逐字传入 |
| ☐ | plot() 按需覆写 | 默认 imshow/plot 不够用时才写 |
| ☐ | 导出链完整 | `function/__init__.py` + 顶级 `__init__.py` 均注册 |
| ☐ | 示例可运行 | `python examples/<序号>_<name>.py` 无误 |
| ☐ | 测试全通过 | `pytest tests/pysimdata/test_<name>.py -v` 全绿 |
| ☐ | Lint 无告警 | `ruff check src/pysimdata/function/<name>.py` 干净 |

---

## 6. CONFIG_KEYS 类型参考

| Python 类型 | CONFIG_KEYS 写法 | JSON 表现形式 | 示例 |
|-------------|-----------------|---------------|------|
| `int` | `int` | 整数 | `"num_points": 10` |
| `float` | `float` | 数字 | `"amplitude": 255.0` |
| `str` | `str` | 字符串 | `"direction": "x"` |
| `bool` | `bool` | 布尔 | `"normalize": true` |
| `tuple` | `tuple` | 数组 → 自动转 tuple | `"shape": [256, 256]` |
| `list` | `list` | 数组 | `"labels": ["a", "b"]` |

> **不在 CONFIG_KEYS 中的参数** 原样保留不做类型转换，但在 `to_config()` 中仍会写出。如果参数是不可 JSON 序列化的（如 `callable`），需要在子类覆写 `to_config()` / `from_config()` 做特殊处理（参考 `FunctionCurve` 的做法）。

---

## 7. 常见问题

### Q: 什么时候需要覆写 `from_config()` ？

**A:** 默认的 `BaseGenerator.from_config()` 已满足大部分需求。只有当参数中包含 **不可 JSON 序列化的类型**（如 `callable`、自定义对象）时，才需要覆写。`FunctionCurve` 的 `func` 参数（字符串函数名 ↔ numpy 函数）是典型例子。

### Q: `_func` 里能用 `self` 吗？

**A:** **不能**。`_func` 是闭包而非方法，所有依赖的数据必须通过参数传入。如果确实需要访问实例状态，考虑把这些状态作为参数传入 `_func`。

### Q: 如何让仿真结果可复现？

**A:** 使用 `rng = np.random.default_rng(seed)` 而非全局 `np.random`。将 `seed` 作为参数并在 `CONFIG_KEYS` 中声明。

### Q: 大尺寸数据生成慢怎么办？

**A:** 在 `_func` 内部尽量用 `np.ogrid` / `np.mgrid` / `np.meshgrid` 矢量化，避免 Python `for` 循环遍历像素。极端情况下可引入 `numba.jit` 装饰 `_func`（基类不感知，直接可用）。
