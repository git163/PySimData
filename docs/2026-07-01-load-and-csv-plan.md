# load() 与 CSV 数据格式 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 pysimdata 新增统一加载入口 `pysimdata.load(dir)`，支持从 save_all 目录整体恢复（有数据读文件+形状校验，无数据按配置生成），数据默认 CSV。

**Architecture:** 在 `BaseGenerator` 上加自动注册表（`__init_subclass__`）、`expected_shape()` 默认推导、多格式 `_read_array`；`save_all` 改 `timestamped=False`+`fmt` 参数；模块级 `load()` 组合以上能力。

**Tech Stack:** Python 3.9+、numpy、pytest。测试命令统一用 `.venv39/bin/python -m pytest`。

**关联设计文档:** `docs/2026-07-01-load-and-csv-design.md`

---

## 文件结构

| 文件 | 职责 | 变更 |
|------|------|------|
| `src/pysimdata/base.py` | 基类核心 | 注册表、`expected_shape`、`_read_array`、`_save_data`(fmt)、`_build_config`(fmt)、`save_all`(签名)、模块级/类级 `load` |
| `src/pysimdata/__init__.py` | 包导出 | 导出 `load`、`BaseGenerator` |
| `scripts/compare_with_python.py` | Py/C++ 对比 | 用注册表取代手工 `TYPE_MAP` |
| `examples/09_load.py` | 新示例 | 演示 save_all → load |
| `tests/pysimdata/test_registry.py` | 测试 | 注册表 |
| `tests/pysimdata/test_expected_shape.py` | 测试 | 形状推导 |
| `tests/pysimdata/test_load.py` | 测试 | load 两场景 + 格式 + 校验 |

---

## Task 1: 自动注册表 + get_generator_class

**Files:**
- Modify: `src/pysimdata/base.py`（`BaseGenerator` 类体内，`CONFIG_KEYS` 定义之后）
- Test: `tests/pysimdata/test_registry.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/pysimdata/test_registry.py`:

```python
"""生成器注册表测试"""
import pytest

from pysimdata.base import BaseGenerator
from pysimdata.function import GaussianGrid, ErfCurve


def test_subclasses_auto_registered():
    """子类定义时自动登记到注册表"""
    assert BaseGenerator.get_generator_class("GaussianGrid") is GaussianGrid
    assert BaseGenerator.get_generator_class("ErfCurve") is ErfCurve


def test_unknown_type_raises():
    """未知 type 抛 ValueError 并提示可用类型"""
    with pytest.raises(ValueError, match="未注册的生成器类型"):
        BaseGenerator.get_generator_class("NotExist")
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv39/bin/python -m pytest tests/pysimdata/test_registry.py -v`
Expected: FAIL（`AttributeError: type object 'BaseGenerator' has no attribute 'get_generator_class'`）

- [ ] **Step 3: 实现注册表**

在 `src/pysimdata/base.py` 的 `BaseGenerator` 中，`CONFIG_KEYS` 定义行之后加入：

```python
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `.venv39/bin/python -m pytest tests/pysimdata/test_registry.py -v`
Expected: PASS（2 passed）

- [ ] **Step 5: 提交**

```bash
git add src/pysimdata/base.py tests/pysimdata/test_registry.py
git commit -m "feat: BaseGenerator 自动注册表与 get_generator_class"
```

---

## Task 2: expected_shape() 默认实现

**Files:**
- Modify: `src/pysimdata/base.py`（属性区之前，新增方法）
- Test: `tests/pysimdata/test_expected_shape.py`

- [ ] **Step 1: 写失败测试**

创建 `tests/pysimdata/test_expected_shape.py`:

```python
"""expected_shape 默认推导测试"""
from pysimdata.function import GaussianGrid, ErfCurve


def test_image_generator_shape_from_shape_param():
    """图像类从 shape 参数推导期望形状"""
    gen = GaussianGrid(shape=(128, 128), num_points=4)
    assert gen.expected_shape() == (128, 128)


def test_curve_generator_shape_from_yshape_numpoints():
    """曲线类从 y_shape + num_points 推导期望形状"""
    gen = ErfCurve(num_points=100, y_shape=50)
    assert gen.expected_shape() == (50, 100)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv39/bin/python -m pytest tests/pysimdata/test_expected_shape.py -v`
Expected: FAIL（`AttributeError: 'GaussianGrid' object has no attribute 'expected_shape'`）

- [ ] **Step 3: 实现 expected_shape**

在 `src/pysimdata/base.py` 的「属性」注释块之前加入：

```python
    # ------------------------------------------------------------------
    # 形状推导（供 load 校验离线数据）
    # ------------------------------------------------------------------
    def expected_shape(self) -> Optional[tuple]:
        """按 params 约定推导输出期望形状；无法推导时返回 None（跳过校验）"""
        p = self._params
        if p.get("shape") is not None:
            return tuple(p["shape"])
        if "y_shape" in p and "num_points" in p:
            return (int(p["y_shape"]), int(p["num_points"]))
        return None
```

- [ ] **Step 4: 运行测试确认通过**

Run: `.venv39/bin/python -m pytest tests/pysimdata/test_expected_shape.py -v`
Expected: PASS（2 passed）

- [ ] **Step 5: 提交**

```bash
git add src/pysimdata/base.py tests/pysimdata/test_expected_shape.py
git commit -m "feat: expected_shape 默认按 params 推导输出形状"
```

---

## Task 3: _read_array 多格式读取（并复用到 _load_offline_data）

**Files:**
- Modify: `src/pysimdata/base.py`（新增 `_read_array`；`_load_offline_data` 改为复用）
- Test: `tests/pysimdata/test_load.py`（本任务先建文件，仅放读取用例）

- [ ] **Step 1: 写失败测试**

创建 `tests/pysimdata/test_load.py`:

```python
"""load 与多格式读取测试"""
import os
import tempfile

import numpy as np
import pytest

from pysimdata.base import BaseGenerator


def test_read_array_csv():
    """读取 csv 还原二维数组"""
    arr = np.arange(6, dtype=float).reshape(2, 3)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.csv")
        np.savetxt(p, arr, delimiter=",")
        out = BaseGenerator._read_array(p)
    np.testing.assert_array_almost_equal(out, arr)


def test_read_array_npy():
    """读取 npy 还原数组"""
    arr = np.arange(4, dtype=float).reshape(2, 2)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.npy")
        np.save(p, arr)
        out = BaseGenerator._read_array(p)
    np.testing.assert_array_almost_equal(out, arr)


def test_read_array_unsupported():
    """不支持的扩展名抛 ValueError"""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "a.xyz")
        with open(p, "w") as f:
            f.write("x")
        with pytest.raises(ValueError, match="不支持的文件格式"):
            BaseGenerator._read_array(p)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `.venv39/bin/python -m pytest tests/pysimdata/test_load.py -v`
Expected: FAIL（`AttributeError: ... has no attribute '_read_array'`）

- [ ] **Step 3: 实现 _read_array 并让 _load_offline_data 复用**

在 `src/pysimdata/base.py` 新增静态方法（放在 `_load_offline_data` 之前）：

```python
    @staticmethod
    def _read_array(path: str, delimiter: str = ",") -> np.ndarray:
        """按扩展名读取数组：csv / npy / npz / 常见图片格式"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"数据文件不存在: {path}")
        ext = os.path.splitext(path)[-1].lower()
        if ext in (".npy", ".npz"):
            return np.load(path)
        if ext == ".csv":
            return np.loadtxt(path, delimiter=delimiter)
        if ext in (".png", ".jpg", ".jpeg", ".tif", ".tiff"):
            from PIL import Image

            return np.array(Image.open(path))
        raise ValueError(f"不支持的文件格式: {ext}")
```

再把现有 `_load_offline_data` 的自定义 loader 之后的读取分支替换为复用：

```python
        custom_loader = self._data_source.get("loader")
        if custom_loader is not None:
            return custom_loader(path)

        delimiter = self._data_source.get("delimiter", ",")
        return self._read_array(path, delimiter=delimiter)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `.venv39/bin/python -m pytest tests/pysimdata/test_load.py -v`
Expected: PASS（3 passed）

- [ ] **Step 5: 回归 + 提交**

Run: `.venv39/bin/python -m pytest tests/ -q`
Expected: 全绿（原 37 + 新增用例）

```bash
git add src/pysimdata/base.py tests/pysimdata/test_load.py
git commit -m "refactor: 抽出 _read_array 多格式读取并复用到 _load_offline_data"
```

---

## Task 4: save_all 支持 fmt/csv + timestamped 默认关 + config 记录 format/data_file

**Files:**
- Modify: `src/pysimdata/base.py`（`_build_config`、`_save_data`、`save_all`）
- Test: `tests/pysimdata/test_load.py`（追加用例）

- [ ] **Step 1: 追加失败测试**

在 `tests/pysimdata/test_load.py` 末尾追加：

```python
from pysimdata.function import GaussianGrid


def test_save_all_csv_default_no_timestamp():
    """默认 fmt=csv、timestamped=False：直接存目标目录，产出 data.csv"""
    gen = GaussianGrid(shape=(32, 32), num_points=4, seed=1)
    gen.generate()
    with tempfile.TemporaryDirectory() as d:
        out = gen.save_all(os.path.join(d, "grid"))
        assert out == os.path.join(d, "grid")  # 未建时间戳子目录
        assert os.path.exists(os.path.join(out, "data.csv"))
        import json
        with open(os.path.join(out, "config.json")) as f:
            cfg = json.load(f)
        assert cfg["format"] == "csv"
        assert cfg["data_file"] == "data.csv"


def test_save_all_npy_option():
    """fmt=npy 时产出 data.npy 且 config 记录 npy"""
    gen = GaussianGrid(shape=(32, 32), num_points=4, seed=1)
    gen.generate()
    with tempfile.TemporaryDirectory() as d:
        out = gen.save_all(os.path.join(d, "grid"), fmt="npy")
        assert os.path.exists(os.path.join(out, "data.npy"))
        import json
        with open(os.path.join(out, "config.json")) as f:
            cfg = json.load(f)
        assert cfg["format"] == "npy"
        assert cfg["data_file"] == "data.npy"
```

- [ ] **Step 2: 运行确认失败**

Run: `.venv39/bin/python -m pytest tests/pysimdata/test_load.py -k save_all -v`
Expected: FAIL（`save_all() got an unexpected keyword argument 'fmt'` 或 config 无 `data_file`）

- [ ] **Step 3: 实现改动**

3a. `_build_config` 增加 `fmt`/`data_file` 参数（替换整个方法）：

```python
    def _build_config(self, fmt: str = "npy", data_file: Optional[str] = None) -> dict:
        """构造配置骨架并填充 params（tuple/list 统一转为 list）"""
        config = {
            "type": self.__class__.__name__,
            "format": fmt,
            "params": {},
        }
        if data_file is not None:
            config["data_file"] = data_file

        # 反向映射: param_name -> json_key
        reverse_keys = {v[0]: k for k, v in self.CONFIG_KEYS.items()}

        for param_name, value in self._params.items():
            json_key = reverse_keys.get(param_name, param_name)
            if isinstance(value, (tuple, list)):
                value = list(value)
            config["params"][json_key] = value

        return config
```

> 注：`to_config()` 仍调用 `self._build_config()`（默认 `fmt="npy"`、无 data_file），保持原 JSON 结构不变，现有 `test_config.py` 不受影响。

3b. `_write_config_file` 增加透传（替换签名与 config 构造行）：

```python
    def _write_config_file(
        self,
        path: str,
        with_timestamp: bool = False,
        fmt: str = "npy",
        data_file: Optional[str] = None,
    ) -> str:
        """将配置写入 JSON 文件，可选追加时间戳字段，返回实际写入路径"""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        config = self._build_config(fmt=fmt, data_file=data_file)
        if with_timestamp:
            config["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        logger.debug("Config saved to %s", path)
        return path
```

> `save_config()` 仍调用 `_write_config_file(path, with_timestamp=False)`（默认 npy、无 data_file），行为不变。

3c. `_save_data` 支持 fmt，返回数据文件名（替换整个方法）：

```python
    def _save_data(self, output_dir: str, name: str, fmt: str = "csv") -> Optional[str]:
        """保存数据数组；fmt=csv 用 savetxt，fmt=npy 用 save。返回数据文件名"""
        if self._data is None:
            return None
        if fmt == "csv":
            data_file = f"{name}.csv"
            np.savetxt(os.path.join(output_dir, data_file), self._data, delimiter=",")
        elif fmt == "npy":
            data_file = f"{name}.npy"
            np.save(os.path.join(output_dir, data_file), self._data)
        else:
            raise ValueError(f"不支持的数据格式: {fmt}")
        logger.debug("Data saved to %s/%s", output_dir, data_file)
        return data_file
```

3d. `save_all` 新签名（替换整个方法）：

```python
    def save_all(
        self,
        output_dir: str,
        name: str = "data",
        timestamped: bool = False,
        fmt: str = "csv",
    ) -> str:
        """
        一次性保存全部产物（数据 + 配置 + 预览图）到指定目录

        Args:
            output_dir: 输出目录 (如 "output/gaussian_grid")
            name: 数据文件名前缀
            timestamped: 是否创建时间戳子目录（默认否）
            fmt: 数据格式，"csv"(默认) 或 "npy"

        Returns:
            实际保存目录路径
        """
        if timestamped:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join(output_dir, ts)
        os.makedirs(output_dir, exist_ok=True)

        data_file = self._save_data(output_dir, name, fmt=fmt)
        self._write_config_file(
            os.path.join(output_dir, "config.json"),
            with_timestamp=True,
            fmt=fmt,
            data_file=data_file,
        )
        self._save_preview(output_dir)

        return output_dir
```

- [ ] **Step 4: 运行确认通过**

Run: `.venv39/bin/python -m pytest tests/pysimdata/test_load.py -k save_all -v`
Expected: PASS（2 passed）

- [ ] **Step 5: 回归 + 提交**

Run: `.venv39/bin/python -m pytest tests/ -q`
Expected: 全绿（`test_config.py` 因 to_config 默认不变而不受影响）

```bash
git add src/pysimdata/base.py tests/pysimdata/test_load.py
git commit -m "feat: save_all 支持 csv/npy 与 data_file 记录，timestamped 默认关"
```

---

## Task 5: load() 统一工厂 + 包导出

**Files:**
- Modify: `src/pysimdata/base.py`（模块级 `load` 函数，放文件末尾）
- Modify: `src/pysimdata/__init__.py`（导出 `load`、`BaseGenerator`）
- Test: `tests/pysimdata/test_load.py`（追加 roundtrip / 两场景 / 校验用例）

- [ ] **Step 1: 追加失败测试**

在 `tests/pysimdata/test_load.py` 末尾追加：

```python
import json
import numpy as np
from pysimdata import load as load_dir


def _write_config_only(d, cfg):
    with open(os.path.join(d, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f)


def test_load_roundtrip_csv():
    """save_all(csv) -> load 数据与 params 一致"""
    gen = GaussianGrid(shape=(32, 32), num_points=4, seed=7)
    gen.generate()
    with tempfile.TemporaryDirectory() as d:
        out = gen.save_all(os.path.join(d, "g"))
        loaded = load_dir(out)
    assert loaded.params["shape"] == (32, 32)
    np.testing.assert_array_almost_equal(loaded.data, gen.data)


def test_load_config_only_generates():
    """目录只有 config.json -> load 触发计算生成"""
    with tempfile.TemporaryDirectory() as d:
        _write_config_only(d, {
            "type": "GaussianGrid",
            "format": "csv",
            "params": {"shape": [32, 32], "num_points": 4, "seed": 7},
        })
        loaded = load_dir(d)
    assert loaded.data.shape == (32, 32)


def test_load_shape_mismatch_raises():
    """数据文件形状与配置不符 -> ValueError"""
    with tempfile.TemporaryDirectory() as d:
        _write_config_only(d, {
            "type": "GaussianGrid",
            "format": "csv",
            "data_file": "data.csv",
            "params": {"shape": [32, 32], "num_points": 4},
        })
        np.savetxt(os.path.join(d, "data.csv"),
                   np.zeros((16, 16)), delimiter=",")  # 错误形状
        with pytest.raises(ValueError, match="形状不匹配"):
            load_dir(d)


def test_load_missing_config_raises():
    """缺 config.json -> FileNotFoundError"""
    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(FileNotFoundError):
            load_dir(d)
```

- [ ] **Step 2: 运行确认失败**

Run: `.venv39/bin/python -m pytest tests/pysimdata/test_load.py -k "load_" -v`
Expected: FAIL（`ImportError: cannot import name 'load'`）

- [ ] **Step 3: 实现 load()**

在 `src/pysimdata/base.py` 文件末尾（类定义之后，模块级）加入：

```python
def load(output_dir: str) -> BaseGenerator:
    """
    从 save_all 输出目录加载生成器：

    - 目录含数据文件：读离线数据并按 expected_shape 校验，直接作为结果数据
    - 目录仅含 config.json：按配置计算生成

    Args:
        output_dir: save_all 保存的目录

    Returns:
        已带数据的生成器实例
    """
    config_path = os.path.join(output_dir, "config.json")
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    cls = BaseGenerator.get_generator_class(config.get("type"))
    gen = cls.from_config(config)

    # 定位数据文件：优先 data_file 字段，回退 data.<ext>
    fmt = config.get("format", "csv")
    data_file = config.get("data_file") or f"data.{'npy' if fmt == 'npy' else 'csv'}"
    data_path = os.path.join(output_dir, data_file)

    if os.path.exists(data_path):
        arr = BaseGenerator._read_array(data_path)
        expected = gen.expected_shape()
        if expected is not None and tuple(arr.shape) != tuple(expected):
            raise ValueError(
                f"数据形状不匹配: 期望 {tuple(expected)}, 实际 {tuple(arr.shape)}"
            )
        gen._data = arr
        logger.debug("Loaded offline data from %s shape %s", data_path, arr.shape)
    else:
        gen.generate()
        logger.debug("No data file; generated from config")

    return gen
```

- [ ] **Step 4: 导出 load**

替换 `src/pysimdata/__init__.py` 内容为：

```python
"""pysimdata - 仿真数据生成器"""
from .base import BaseGenerator, load
from .function import (
    GaussianGrid,
    GaussianBeam,
    FunctionCurve,
    ErfCurve,
    TanhCurve,
    CoshCurve,
    ExponentialDecay,
    BilateralGaussian,
)

__all__ = [
    "BaseGenerator",
    "load",
    "GaussianGrid",
    "GaussianBeam",
    "FunctionCurve",
    "ErfCurve",
    "TanhCurve",
    "CoshCurve",
    "ExponentialDecay",
    "BilateralGaussian",
]

__version__ = "0.1.0"
```

- [ ] **Step 5: 运行确认通过 + 全量回归**

Run: `.venv39/bin/python -m pytest tests/pysimdata/test_load.py -v`
Expected: PASS（全部用例）

Run: `.venv39/bin/python -m pytest tests/ -q`
Expected: 全绿

- [ ] **Step 6: 提交**

```bash
git add src/pysimdata/base.py src/pysimdata/__init__.py tests/pysimdata/test_load.py
git commit -m "feat: 新增统一加载入口 pysimdata.load 支持目录整体恢复"
```

---

## Task 6: compare_with_python.py 改用注册表

**Files:**
- Modify: `scripts/compare_with_python.py:15-35`（imports + 手工 `TYPE_MAP` + 用法处）

- [ ] **Step 1: 替换 imports 与 TYPE_MAP**

将 `scripts/compare_with_python.py` 顶部的 `from pysimdata.function import (...)` 块与整个 `TYPE_MAP = {...}` 字典删除，替换为：

```python
from pysimdata.base import BaseGenerator
```

- [ ] **Step 2: 替换分派用法**

在 `generate_python()` 中，将 `cls = TYPE_MAP[config["type"]]` 改为：

```python
    cls = BaseGenerator.get_generator_class(config["type"])
```

> 注：`import pysimdata`（或 `pysimdata.function`）仍需触发一次，以确保子类被定义并自动注册。若脚本未 import function 包，在 `from pysimdata.base import BaseGenerator` 后补一行 `import pysimdata.function  # noqa: F401 触发子类注册`。

- [ ] **Step 3: 验证脚本可跑（若已有 C++ 构建）**

Run: `.venv39/bin/python -c "from pysimdata.base import BaseGenerator; import pysimdata.function; print(BaseGenerator.get_generator_class('GaussianGrid').__name__)"`
Expected: 打印 `GaussianGrid`

- [ ] **Step 4: 提交**

```bash
git add scripts/compare_with_python.py
git commit -m "refactor: compare 脚本改用注册表取代手工 TYPE_MAP"
```

---

## Task 7: examples 适配 + 新增 load 示例

**Files:**
- 说明：8 个 `examples/0*.py` 已在上一轮把 `gen.save(` 改为 `gen.save_all(`。因 `save_all` 的 `timestamped` 默认由 True 变 False，行为自动变为「直接存到 `output/xxx`」，**无需改代码**。
- Create: `examples/09_load.py`

- [ ] **Step 1: 新增 load 示例**

创建 `examples/09_load.py`:

```python
"""load: 从 save_all 目录整体恢复（配置 + 数据）"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata import GaussianGrid, load

# 先生成并保存（默认 csv、无时间戳）
gen = GaussianGrid(shape=(128, 128), num_points=9, seed=42)
gen.generate()
out = gen.save_all("output/load_demo")
print(f"saved to: {out}")

# 从目录整体恢复：数据直接来自 data.csv，不重算
restored = load(out)
print(f"restored data shape: {restored.data.shape}")
print(f"restored params: {restored.params}")
```

- [ ] **Step 2: 运行示例验证**

Run: `.venv39/bin/python examples/09_load.py`
Expected: 打印 saved 路径、`restored data shape: (128, 128)`、params 字典，无异常

- [ ] **Step 3: 运行全部 examples 回归**

Run: `.venv39/bin/python run_examples.py`
Expected: 所有示例（含 09）正常，`output/` 下各目录直接产出 `data.csv`/`config.json`/`preview.png`（无时间戳子目录）

- [ ] **Step 4: 提交**

```bash
git add examples/09_load.py
git commit -m "docs: 新增 load 示例演示目录整体恢复"
```

---

## Task 8: 全量回归 + 文档状态更新

**Files:**
- Modify: `docs/2026-07-01-load-and-csv-design.md`（状态改「已实施」）

- [ ] **Step 1: 全量测试**

Run: `.venv39/bin/python -m pytest tests/ -v`
Expected: 全绿（原 37 + registry/expected_shape/load 新增用例）

- [ ] **Step 2: 冒烟导入**

Run: `.venv39/bin/python -c "import pysimdata; print(pysimdata.load, pysimdata.BaseGenerator)"`
Expected: 打印 load 函数与 BaseGenerator 类，无异常

- [ ] **Step 3: 更新设计文档状态**

将 `docs/2026-07-01-load-and-csv-design.md` 头部 `- 状态: 评审中` 改为 `- 状态: 已实施`。

- [ ] **Step 4: 提交**

```bash
git add docs/2026-07-01-load-and-csv-design.md
git commit -m "docs: 标记 load 与 CSV 设计为已实施"
```

---

## 自检记录

- **Spec 覆盖**：load 两场景(Task5) / 注册表(Task1,6) / expected_shape 校验(Task2,5) / csv 默认+npy 可选(Task4) / timestamped 默认关(Task4) / data_file 字段(Task4,5) / _read_array 复用(Task3) / 导出(Task5) / 示例(Task7) —— 全部有对应任务。
- **占位符**：无 TBD/TODO，所有代码步骤均给出完整代码。
- **类型一致性**：`_save_data` 返回 `data_file` → `save_all` 传入 `_write_config_file` → `_build_config` 写入 config → `load` 读取 `data_file`，字段名贯穿一致；`get_generator_class` / `expected_shape` / `_read_array` 签名在定义与调用处一致。
- **回归保障**：`to_config()`/`save_config()` 均沿用默认参数，原 `test_config.py` 行为不变。

