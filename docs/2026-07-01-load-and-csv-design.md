# 统一加载入口 load() 与 CSV 数据格式设计

- 日期: 2026-07-01
- 作者: git163
- 状态: 已实施
- 关联: src/pysimdata/base.py, src/pysimdata/__init__.py, src/pysimdata/function/*, scripts/compare_with_python.py

## 背景

`BaseGenerator` 目前支持「从配置文件计算生成仿真数据」的路径（`from_config()` → `generate()`），但存在两个缺口：

1. **无法从已保存的产物目录整体恢复**：`save_all()` 会把 `config.json` + 数据文件保存到目录，但没有对称的加载入口把它们一起读回来；`data_source`（离线数据）能力只能在代码里手工传参，配置文件无法描述，`from_config`/`to_config` 也不处理它。
2. **数据格式与 C++ 侧不统一**：Python 默认存 `.npy`，而 C++（`examples_cplus/09_from_config`）输出 `.csv`。CSV 可读、且能让两端数据格式一致，更适合作为默认。

同时用户提出两点行为调整：`save_all()` 默认不再生成时间戳子目录；加载入口需要「有数据就读文件并校验、没数据就按配置计算」的智能回退。

## 目标

- 新增统一加载入口 `pysimdata.load(output_dir)`，一个函数覆盖两种场景：
  - **场景一（计算）**：目录里只有 `config.json` → 按配置 `generate()` 计算生成。
  - **场景二（读取）**：目录里同时有 `config.json` 和数据文件 → 读离线数据，并与配置推导出的期望形状做校验，用文件数据。
- 数据导出/导入默认使用 CSV，保留 npy 可选，由 config 的 `format` 字段驱动。
- `save_all()` 默认 `timestamped=False`，需要时显式传 `timestamped=True`。
- 用自动注册表消除手工维护的 `type→class` 映射。
- **非目标**：不改各生成器的计算逻辑与 `__init__` 签名；不改 `from_config`/`to_config`/`generate`/`plot` 等既有接口的语义；C++ 侧对 `format` 的同步不在本次范围。

## 方案

### 架构：两条对称的数据获取路径

```
场景一（计算）:  config.json ──from_config()──> 实例(params) ──generate()──> data(算出)

场景二（读取）:  output_dir/ ─────load()──────> 实例(params) + data(直接读自文件, 经形状校验)
                  ├ config.json
                  └ data.csv (或 data.npy)

load() 统一入口逻辑:
    读 config.json
    cls = 注册表[config["type"]]
    gen = cls.from_config(config)          # 恢复 params
    data_path = 定位数据文件(output_dir, config)
    if data_path 存在:
        arr = _read_array(data_path, fmt)  # 读离线数据
        校验 arr.shape == gen.expected_shape()   # 不符则抛异常
        gen._data = arr                    # 用文件数据，不重算
    else:
        gen.generate()                     # 只有配置 → 按参数计算
    return gen
```

`load()` 返回的实例：`.data` 直接可用（可 `plot`、`to_config`），且保留重算能力（再调 `generate()` 会按 params 覆盖计算）。

### 关键设计点

1. **自动注册表（`__init_subclass__`）**
   - `BaseGenerator` 维护类级 `_REGISTRY: Dict[str, type]`；`__init_subclass__` 在每个子类定义时自动执行 `_REGISTRY[cls.__name__] = cls`。
   - 提供 `BaseGenerator.get_generator_class(type_name) -> type`，未注册时抛 `ValueError`（提示可用类型）。
   - 对使用者透明、零维护：新增生成器无需改任何映射。`scripts/compare_with_python.py` 改用它，删除手工 `TYPE_MAP`。

2. **`expected_shape()` 默认实现（基类，按 params 约定推导）**
   ```python
   def expected_shape(self) -> Optional[tuple]:
       p = self._params
       if p.get("shape") is not None:                 # 图像类: GaussianGrid/GaussianBeam/BilateralGaussian/ExponentialDecay
           return tuple(p["shape"])
       if "y_shape" in p and "num_points" in p:        # 曲线类: FunctionCurve/ErfCurve/TanhCurve/CoshCurve
           return (int(p["y_shape"]), int(p["num_points"]))
       return None                                     # 无法推导 → 跳过校验
   ```
   - 默认实现即可覆盖全部 8 个现有生成器，子类无需改动；形状规则特殊的未来生成器可重写。
   - 校验：`expected_shape()` 返回 `None` 时跳过；否则 `arr.shape` 必须相等，不符抛 `ValueError`（打印期望 vs 实际）。

3. **`save_all()` 签名调整**
   ```python
   def save_all(self, output_dir, name="data", timestamped=False, fmt="csv") -> str
   ```
   - `timestamped` 默认 `False`（不再自动建时间戳子目录）。
   - `fmt` 默认 `"csv"`，可选 `"npy"`（参数名用 `fmt` 避免遮蔽内置 `format`）；数据存为 `{name}.{ext}`（`csv`→`.csv`，`npy`→`.npy`）。
   - 写入的 `config.json` 用 `format` 字段记录实际格式与数据文件名，供 `load()` 精确定位。

4. **多格式数据读写（去重复用）**
   - 抽出 `_read_array(path, fmt=None) -> np.ndarray`：按扩展名/`fmt` 分派——`.csv`(`np.loadtxt`, 逗号分隔)、`.npy/.npz`(`np.load`)、图片(`PIL`)。现有 `_load_offline_data()` 的多格式逻辑复用它，避免重复。
   - `_save_data(output_dir, name, fmt)`：`csv`→`np.savetxt(delimiter=",")`；`npy`→`np.save`。

### 接口 / 数据结构

**config.json 格式（新增/沿用字段）**
```json
{
  "type": "GaussianGrid",
  "format": "csv",
  "data_file": "data.csv",
  "params": { "shape": [256, 256], "mean": 0, "std": 1, "num_points": 9 }
}
```
- `format`：数据格式（`csv`/`npy`），已有字段，本次赋予实际含义。
- `data_file`：数据文件名，`save_all()` 写入；`load()` 优先按它定位，缺失则回退到 `data.<ext>`（兼容旧配置）。

**新增/变更接口一览**

| 接口 | 位置 | 说明 |
|------|------|------|
| `pysimdata.load(output_dir)` | `__init__.py` / `base.py` | 统一工厂入口，返回带数据的实例 |
| `BaseGenerator.get_generator_class(type_name)` | `base.py` | 按 type 查注册表 |
| `BaseGenerator.expected_shape()` | `base.py` | 按 params 推导期望形状，可重写 |
| `BaseGenerator._read_array(path, fmt)` | `base.py` | 多格式读数组（私有，复用） |
| `save_all(..., timestamped=False, fmt="csv")` | `base.py` | 时间戳默认关、新增 fmt |

## 错误处理

- 目录不存在 / `config.json` 缺失 → `FileNotFoundError`。
- `config["type"]` 未注册 → `ValueError`（列出可用类型）。
- 数据文件存在但格式不支持 → `ValueError`。
- 数据形状与 `expected_shape()` 不符 → `ValueError`（打印期望 vs 实际 shape）。
- 上述读取/解析处均 try/except 并记录英文日志，异常向上抛出。

## 影响范围

- `src/pysimdata/base.py`：注册表 + `__init_subclass__`、`expected_shape()`、`_read_array()`、`_save_data` 支持 csv、`save_all()` 签名调整、`_load_offline_data` 复用 `_read_array`。
- `src/pysimdata/__init__.py`：导出 `load`。
- `src/pysimdata/function/*`：一般无需改（默认 `expected_shape` 已覆盖）；仅在自动注册钩子生效上验证。
- `scripts/compare_with_python.py`：改用注册表，删除手工 `TYPE_MAP`。
- `examples/`：8 个示例因 `timestamped` 默认 False 行为变化（直接存到 `output/xxx`）；新增 1 个 `load()` 示例。
- `tests/`：新增用例（见下）。

## 测试计划

1. **CSV roundtrip**：`save_all(fmt="csv")` → `load()` → `data`/`params`/`to_config()` 与原实例逐项一致。
2. **npy roundtrip**：`fmt="npy"` 同样一致。
3. **场景一（仅配置）**：目录只放 `config.json`（无数据文件）→ `load()` 触发 `generate()`，形状正确。
4. **场景二（配置+数据）**：`load()` 读文件数据、不重算（可用 seed 或标记数据验证未被覆盖）。
5. **形状校验失败**：故意放入形状不符的数据文件 → `load()` 抛 `ValueError`。
6. **注册表分派**：各 `type` 字符串能正确映射到类；未知 type 抛错。
7. **timestamped 默认**：`save_all()` 默认直接存目标目录、不建时间戳子目录。

## 验证

- `.venv39/bin/python -m pytest tests/ -q` 全绿。
- `.venv39/bin/python run_examples.py` 正常产出；新增 `load()` 示例可读回并 `plot`。
- 手动核对一个 `save_all` 目录经 `load()` 恢复后 `to_config()` 与原配置一致。
