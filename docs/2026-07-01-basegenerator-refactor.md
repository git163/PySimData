# BaseGenerator 接口重命名与执行逻辑封装重构

- 日期: 2026-07-01
- 作者: git163
- 状态: 已实施
- 关联: src/pysimdata/base.py, src/pysimdata/function/function_curve.py

## 背景

`BaseGenerator` 是 8 个仿真数据生成器的公共基类。当前实现存在几处影响可读性与维护性的问题（不影响功能）：

1. **命名不精确**：`save()` 一次做三件事（存数据 + 配置 + 预览图），名字过泛，与单项方法层级不清；`save_image()` 实际保存的是预览图（与产出的 `preview.png` 同源）；`load_config_file()` 是 `from_config()` 的内部文件读取步骤，却暴露为公开方法；`save()` 的 `enable_timestamp` 参数偏冗长。
2. **逻辑重复**：`save()` 内部写 config 的逻辑与 `save_config()` 重复；`to_config()` 的 `{type, format, params}` 骨架构造在基类与 `FunctionCurve` 中重复；`plot()` 与 `save_image()` 中「二维 imshow / 一维 plot」判断重复。
3. **函数过长**：`save()` 混合了存数据、存配置、存预览图三件事，未拆分。
4. **死代码**：`self._config` 字段定义后从未被读写。

目标：在**完全不改变功能**的前提下，重命名不清晰的接口、封装重复逻辑、清理死代码，使基类更清晰、更易被其他项目移植。

## 目标

- 重命名语义不精确的接口，并同步更新所有调用点（硬重命名，不保留旧名别名）。
- 封装重复逻辑为私有方法，消除基类内部及与 `FunctionCurve` 的重复代码。
- 清理死代码。
- **非目标**：不改 `__init__(func, data_source, **params)` 签名（全部子类依赖）；不重命名 `_data`/`_params`/`_func`/`_data_source`（被 6 个子类的 `plot()` 直接访问，命名已清晰，重命名无收益且波及全部子类）；不改 `from_config`/`to_config`/`generate`/`plot`/`data`/`params` 等社区约定命名。

## 方案（已落地）

### 一、接口重命名对照表

| 原名 | 新名 | 理由 |
|------|------|------|
| `save(..., enable_timestamp=True)` | `save_all(..., timestamped=True)` | 与 `save_config`/`save_preview` 形成一致体系：`save_all`=存全部产物，另两个=存单项；`timestamped` 作为 bool 参数用形容词更简洁 |
| `save_image(path)` | `save_preview(path)` | 保存的是预览图，与产出的 `preview.png` 语义一致；此前无任何外部调用 |
| `load_config_file(path)` (classmethod, public) | `_load_config_file(path)` (classmethod, protected) | 它是 `from_config()` 的内部文件读取步骤，外部不应直接调用；私有化，子类仍可调用 |

> 保留 `from_config` / `to_config` / `save_config` / `generate` / `plot` / `data` / `params`：清晰且约定俗成，重命名反而降低通用性。

### 二、封装的私有方法（新增，消除重复）

- `_render(ax)`：统一「二维 `imshow` / 一维 `plot`」渲染逻辑，供 `plot()` 与 `save_preview()` 复用；内部用 `self.data` property 复用 None 检查。
- `_build_config()`：构造 `{type, format, params}` 骨架并填充 `params`（含 tuple→list 转换），供 `to_config()` 使用；`FunctionCurve.to_config()` 复用骨架后再追加 `func` 字段。
- `_write_config_file(path, with_timestamp=False)`：写 config JSON，可选追加 `timestamp`，供 `save_config()`（无时间戳）与 `save_all()`（带时间戳）复用。
- `_save_data(output_dir, name)` / `_save_preview(output_dir)`：将 `save_all()` 中存 npy、存 preview.png（含 matplotlib 的 try/except ImportError）步骤各自抽出。

### 三、`save_all()` 重构后结构

```python
def save_all(self, output_dir, name="data", timestamped=True):
    if timestamped:
        output_dir = os.path.join(output_dir, datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(output_dir, exist_ok=True)
    self._save_data(output_dir, name)
    self._write_config_file(os.path.join(output_dir, "config.json"), with_timestamp=True)
    self._save_preview(output_dir)
    return output_dir
```

### 四、执行逻辑与死代码

- 删除 `__init__` 中的 `self._config`（死代码）。
- `generate()` / `_load_offline_data()`：`_load_offline_data()` 改为返回数组由 `generate()` 赋值，offline/func 分支更清晰；行为不变。
- `from_config()`：`extra_params` 提取改用字典推导，等价且更易读。

## 影响范围（实际改动）

- `src/pysimdata/base.py`：主重构（上述全部）。
- `src/pysimdata/function/function_curve.py`：`cls.load_config_file` → `cls._load_config_file`；`to_config()` 复用基类 `_build_config()` 骨架（输出 JSON 逐字段一致）。
- `examples/*.py`（8 个）：`gen.save(...)` → `gen.save_all(...)`。
- tests / scripts 无需改动（`save_config`/`from_config`/`to_config` 名称保留；无处调用 `save_image`/`load_config_file`）。

## 验证结果

- `PYTHONPATH=src pytest tests/ -q` → **37 passed**。
- `run_examples.py`（python3.11）→ 8 个 examples 全部正常产出 `data.npy`/`config.json`/`preview.png`。
- 补测：`save_preview()` 生成图片正常；`FunctionCurve.to_config()` 逐字段与重构前一致；`save_config → from_config → generate` roundtrip 数据一致；`save_all()` 默认时间戳目录产物齐全。

> 注：本机默认 `python`(3.14) 的 numpy 安装损坏（缺 `np.sin`/`__version__`），需用 python3.11 运行 examples；与本次重构无关。
