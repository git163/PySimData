# 仿真数据生成器框架实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现仿真数据生成器框架，支持高斯点阵、高斯束斑、函数曲线等多种场景

**Architecture:** 基类 + 子类继承架构，底层 func 内部定义，支持离线数据导入

**Tech Stack:** Python 3.9+, numpy, scipy, PIL, matplotlib

---

## File Structure

```
src/pysimdata/
├── __init__.py              # 修改: 导出所有类
├── base.py                  # 新建: 基类 BaseGenerator
├── gaussian/
│   ├── __init__.py         # 新建
│   ├── grid.py            # 新建: GaussianGrid
│   └── beam.py           # 新建: GaussianBeam
└── function/
    ├── __init__.py        # 新建
    ├── curve.py          # 新建: FunctionCurve
    ├── special.py       # 新建: ErfCurve, TanhCurve, CoshCurve
    └── decay.py         # 新建: ExponentialDecay, BilateralGaussian
```

---

### Task 1: 创建基类 BaseGenerator

**Files:**
- Create: `src/pysimdata/base.py`
- Test: `tests/pysimdata/test_base.py`

- [ ] **Step 1: 创建测试文件**

```python
# tests/pysimdata/test_base.py
import numpy as np
import pytest
from pysimdata.base import BaseGenerator


def test_base_generator_requires_func_or_data_source():
    """必须提供 func 或 data_source"""
    with pytest.raises(ValueError, match="必须提供 func 或 data_source"):
        BaseGenerator()


def test_base_generator_with_func():
    """使用 func 生成数据"""
    def mock_func(x, y):
        return np.array([[x, y]])

    gen = BaseGenerator(func=mock_func, x=1, y=2)
    result = gen.generate()
    assert result.shape == (1, 2)


def test_base_generator_data_property():
    """data 属性返回生成的数据"""
    def mock_func(value):
        return np.array([[value]])

    gen = BaseGenerator(func=mock_func, value=42)
    gen.generate()
    assert gen.data[0, 0] == 42


def test_base_generator_data_property_before_generate():
    """generate 前访问 data 应抛出异常"""
    def mock_func():
        return np.array([[1]])

    gen = BaseGenerator(func=mock_func)
    with pytest.raises(ValueError, match="请先调用 generate"):
        _ = gen.data
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/pysimdata/test_base.py -v`
Expected: FAIL (BaseGenerator 未定义)

- [ ] **Step 3: 实现基类**

```python
# src/pysimdata/base.py
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
        self._func = func
        self._data_source = data_source
        self._params = params
        self._data: np.ndarray | None = None

    def generate(self) -> np.ndarray:
        """生成仿真数据"""
        if self._data_source is not None:
            self._load_offline_data()
        elif self._func is not None:
            self._data = self._func(**self._params)
        else:
            raise ValueError("必须提供 func 或 data_source")
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
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/pysimdata/test_base.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/pysimdata/base.py tests/pysimdata/test_base.py
git commit -m "feat: 添加 BaseGenerator 基类"
```

---

### Task 2: 实现 GaussianGrid

**Files:**
- Create: `src/pysimdata/gaussian/__init__.py`
- Create: `src/pysimdata/gaussian/grid.py`
- Test: `tests/pysimdata/test_gaussian.py`

- [ ] **Step 1: 创建测试文件**

```python
# tests/pysimdata/test_gaussian.py
import numpy as np
import pytest
from pysimdata.gaussian import GaussianGrid


def test_gaussian_grid_default():
    """默认参数生成"""
    gen = GaussianGrid()
    data = gen.generate()
    assert data.shape == (256, 256)


def test_gaussian_grid_custom_params():
    """自定义参数"""
    gen = GaussianGrid(shape=(128, 128), mean=0, std=1, num_points=5, seed=42)
    data = gen.generate()
    assert data.shape == (128, 128)


def test_gaussian_grid_data_property():
    """data 属性"""
    gen = GaussianGrid()
    _ = gen.generate()
    assert gen.data.shape == (256, 256)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/pysimdata/test_gaussian.py::test_gaussian_grid_default -v`
Expected: FAIL

- [ ] **Step 3: 实现 GaussianGrid**

```python
# src/pysimdata/gaussian/__init__.py
from .grid import GaussianGrid

__all__ = ["GaussianGrid"]
```

```python
# src/pysimdata/gaussian/grid.py
"""高斯点阵生成器"""
import numpy as np

from ..base import BaseGenerator


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

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/pysimdata/test_gaussian.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/pysimdata/gaussian/ tests/pysimdata/test_gaussian.py
git commit -m "feat: 添加 GaussianGrid 高斯点阵生成器"
```

---

### Task 3: 实现 GaussianBeam

**Files:**
- Modify: `src/pysimdata/gaussian/beam.py`
- Test: `tests/pysimdata/test_gaussian.py`

- [ ] **Step 1: 添加测试**

```python
def test_gaussian_beam_default():
    """默认参数生成"""
    from pysimdata.gaussian import GaussianBeam

    gen = GaussianBeam()
    data = gen.generate()
    assert data.shape == (256, 256)
    # 中心值应接近 amplitude
    assert data[128, 128] > 200


def test_gaussian_beam_custom():
    """自定义参数"""
    from pysimdata.gaussian import GaussianBeam

    gen = GaussianBeam(shape=(128, 128), sigma=10, amplitude=200, center=(64, 64))
    data = gen.generate()
    assert data.shape == (128, 128)
    assert data[64, 64] == 200
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/pysimdata/test_gaussian.py::test_gaussian_beam_default -v`
Expected: FAIL

- [ ] **Step 3: 实现 GaussianBeam**

```python
# src/pysimdata/gaussian/beam.py
"""高斯束斑生成器"""
import numpy as np

from ..base import BaseGenerator


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

```python
# src/pysimdata/gaussian/__init__.py
from .grid import GaussianGrid
from .beam import GaussianBeam

__all__ = ["GaussianGrid", "GaussianBeam"]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/pysimdata/test_gaussian.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/pysimdata/gaussian/beam.py tests/pysimdata/test_gaussian.py
git commit -m "feat: 添加 GaussianBeam 高斯束斑生成器"
```

---

### Task 4: 实现 FunctionCurve

**Files:**
- Create: `src/pysimdata/function/__init__.py`
- Create: `src/pysimdata/function/curve.py`
- Test: `tests/pysimdata/test_function.py`

- [ ] **Step 1: 创建测试文件**

```python
# tests/pysimdata/test_function.py
import numpy as np
from pysimdata.function import FunctionCurve


def test_function_curve_sin():
    """sin 函数"""
    gen = FunctionCurve(func=np.sin, x_range=(0, 2 * np.pi), num_points=50, amplitude=1.0)
    data = gen.generate()
    assert data.shape == (100, 50)


def test_function_curve_cos():
    """cos 函数"""
    gen = FunctionCurve(func=np.cos, x_range=(0, 2 * np.pi), num_points=50)
    data = gen.generate()
    assert data.shape == (100, 50)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/pysimdata/test_function.py::test_function_curve_sin -v`
Expected: FAIL

- [ ] **Step 3: 实现 FunctionCurve**

```python
# src/pysimdata/function/__init__.py
from .curve import FunctionCurve

__all__ = ["FunctionCurve"]
```

```python
# src/pysimdata/function/curve.py
"""基础函数曲线生成器"""
import numpy as np

from ..base import BaseGenerator


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

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/pysimdata/test_function.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/pysimdata/function/ tests/pysimdata/test_function.py
git commit -m "feat: 添加 FunctionCurve 函数曲线生成器"
```

---

### Task 5: 实现特殊函数 (ErfCurve, TanhCurve, CoshCurve)

**Files:**
- Modify: `src/pysimdata/function/special.py`
- Modify: `src/pysimdata/function/__init__.py`
- Test: `tests/pysimdata/test_function.py`

- [ ] **Step 1: 添加测试**

```python
def test_erf_curve():
    """误差函数"""
    from pysimdata.function import ErfCurve

    gen = ErfCurve(x_range=(-3, 3), num_points=50)
    data = gen.generate()
    assert data.shape == (100, 50)


def test_tanh_curve():
    """双曲正切"""
    from pysimdata.function import TanhCurve

    gen = TanhCurve(x_range=(-3, 3), num_points=50)
    data = gen.generate()
    assert data.shape == (100, 50)


def test_cosh_curve():
    """双曲余弦"""
    from pysimdata.function import CoshCurve

    gen = CoshCurve(x_range=(-2, 2), num_points=50)
    data = gen.generate()
    assert data.shape == (100, 50)
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/pysimdata/test_function.py::test_erf_curve -v`
Expected: FAIL

- [ ] **Step 3: 实现特殊函数**

```python
# src/pysimdata/function/special.py
"""特殊函数生成器"""
import numpy as np
from scipy.special import erf

from ..base import BaseGenerator


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

```python
# src/pysimdata/function/__init__.py
from .curve import FunctionCurve
from .special import ErfCurve, TanhCurve, CoshCurve

__all__ = ["FunctionCurve", "ErfCurve", "TanhCurve", "CoshCurve"]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/pysimdata/test_function.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/pysimdata/function/special.py tests/pysimdata/test_function.py
git commit -m "feat: 添加 ErfCurve, TanhCurve, CoshCurve 特殊函数生成器"
```

---

### Task 6: 实现衰减函数 (ExponentialDecay, BilateralGaussian)

**Files:**
- Create: `src/pysimdata/function/decay.py`
- Modify: `src/pysimdata/function/__init__.py`
- Test: `tests/pysimdata/test_function.py`

- [ ] **Step 1: 添加测试**

```python
def test_exponential_decay():
    """单边指数衰减"""
    from pysimdata.function import ExponentialDecay

    gen = ExponentialDecay(shape=(64, 64), tau=10, amplitude=255, direction="x")
    data = gen.generate()
    assert data.shape == (64, 64)


def test_bilateral_gaussian():
    """双边高斯分布"""
    from pysimdata.function import BilateralGaussian

    gen = BilateralGaussian(shape=(64, 64), sigma=10, amplitude=255)
    data = gen.generate()
    assert data.shape == (64, 64)
    assert data[32, 32] == 255  # 中心最大
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest tests/pysimdata/test_function.py::test_exponential_decay -v`
Expected: FAIL

- [ ] **Step 3: 实现衰减函数**

```python
# src/pysimdata/function/decay.py
"""衰减函数生成器"""
import numpy as np

from ..base import BaseGenerator


class ExponentialDecay(BaseGenerator):
    """单边指数衰减生成器"""

    def __init__(
        self,
        shape: tuple[int, int] = (256, 256),
        tau: float = 10.0,
        amplitude: float = 255.0,
        direction: str = "x",
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

```python
# src/pysimdata/function/__init__.py
from .curve import FunctionCurve
from .special import ErfCurve, TanhCurve, CoshCurve
from .decay import ExponentialDecay, BilateralGaussian

__all__ = [
    "FunctionCurve",
    "ErfCurve",
    "TanhCurve",
    "CoshCurve",
    "ExponentialDecay",
    "BilateralGaussian",
]
```

- [ ] **Step 4: 运行测试验证通过**

Run: `pytest tests/pysimdata/test_function.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/pysimdata/function/decay.py tests/pysimdata/test_function.py
git commit -m "feat: 添加 ExponentialDecay, BilateralGaussian 衰减函数生成器"
```

---

### Task 7: 更新主模块导出

**Files:**
- Modify: `src/pysimdata/__init__.py`

- [ ] **Step 1: 更新导出**

```python
# src/pysimdata/__init__.py
"""pysimdata - 仿真数据生成器"""
from .gaussian import GaussianGrid, GaussianBeam
from .function import (
    FunctionCurve,
    ErfCurve,
    TanhCurve,
    CoshCurve,
    ExponentialDecay,
    BilateralGaussian,
)

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

- [ ] **Step 2: 验证导入**

```bash
.venv/bin/python -c "from pysimdata import GaussianGrid, GaussianBeam, FunctionCurve, ErfCurve, TanhCurve, CoshCurve, ExponentialDecay, BilateralGaussian; print('OK')"
```

- [ ] **Step 3: Commit**

```bash
git add src/pysimdata/__init__.py
git commit -m "feat: 更新主模块导出"
```

---

### Task 8: 最终测试

**Files:**
- Run: 所有测试

- [ ] **Step 1: 运行所有测试**

```bash
pytest -v
```

- [ ] **Step 2: 验证所有功能**

```bash
.venv/bin/python -c "
import numpy as np
from pysimdata import GaussianGrid, GaussianBeam, FunctionCurve, ErfCurve

# 测试高斯点阵
g = GaussianGrid(shape=(64, 64), num_points=5)
print('GaussianGrid:', g.generate().shape)

# 测试高斯束斑
g = GaussianBeam(shape=(64, 64), sigma=5)
print('GaussianBeam:', g.generate().shape)

# 测试函数曲线
f = FunctionCurve(func=np.sin, num_points=50)
print('FunctionCurve:', f.generate().shape)

# 测试 erf
e = ErfCurve(num_points=50)
print('ErfCurve:', e.generate().shape)
"
```

- [ ] **Step 3: Commit**

```bash
git add .
git commit -m "feat: 完成仿真数据生成器框架"
```