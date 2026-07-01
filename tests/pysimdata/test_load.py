"""load 与多格式读取测试"""
import json
import os
import tempfile

import numpy as np
import pytest

from pysimdata import FunctionCurve, load as load_dir
from pysimdata.base import BaseGenerator
from pysimdata.function import GaussianGrid


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


def test_save_all_csv_default_no_timestamp():
    """默认 fmt=csv、timestamped=False：直接存目标目录，产出 data.csv"""
    gen = GaussianGrid(shape=(32, 32), num_points=4, seed=1)
    gen.generate()
    with tempfile.TemporaryDirectory() as d:
        out = gen.save_all(os.path.join(d, "grid"))
        assert out == os.path.join(d, "grid")  # 未建时间戳子目录
        assert os.path.exists(os.path.join(out, "data.csv"))
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
        with open(os.path.join(out, "config.json")) as f:
            cfg = json.load(f)
        assert cfg["format"] == "npy"
        assert cfg["data_file"] == "data.npy"


def test_save_all_functioncurve_keeps_func():
    """FunctionCurve 经 save_all 后 config 仍保留 func 字段"""
    gen = FunctionCurve()
    gen.generate()
    with tempfile.TemporaryDirectory() as d:
        out = gen.save_all(os.path.join(d, "fc"))
        with open(os.path.join(out, "config.json")) as f:
            cfg = json.load(f)
        assert "func" in cfg["params"]


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


def test_load_roundtrip_npy():
    """save_all(fmt='npy') -> load 数据与 params 一致"""
    gen = GaussianGrid(shape=(32, 32), num_points=4, seed=7)
    gen.generate()
    with tempfile.TemporaryDirectory() as d:
        out = gen.save_all(os.path.join(d, "g"), fmt="npy")
        loaded = load_dir(out)
    assert loaded.params["shape"] == (32, 32)
    np.testing.assert_array_almost_equal(loaded.data, gen.data)


def test_load_uses_file_data_not_regenerate():
    """有数据文件时 load 使用文件内容，而非按配置重算"""
    gen = GaussianGrid(shape=(16, 16), num_points=4, seed=3)
    gen.generate()
    with tempfile.TemporaryDirectory() as d:
        out = gen.save_all(os.path.join(d, "g"))
        # 篡改数据文件为可识别常量（与配置同形状），确认 load 读的是文件内容
        marker = np.full((16, 16), 7.0)
        np.savetxt(os.path.join(out, "data.csv"), marker, delimiter=",")
        loaded = load_dir(out)
    np.testing.assert_array_almost_equal(loaded.data, marker)


def test_load_functioncurve_roundtrip_keeps_func():
    """FunctionCurve 经 save_all -> load 后，to_config 仍保留正确的 func 名"""
    gen = FunctionCurve()  # 默认 func=sin
    gen.generate()
    with tempfile.TemporaryDirectory() as d:
        out = gen.save_all(os.path.join(d, "fc"))
        loaded = load_dir(out)
    assert loaded.to_config()["params"]["func"] == "sin"


def test_load_missing_type_raises():
    """config.json 缺少 type 字段 -> ValueError"""
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "config.json"), "w", encoding="utf-8") as f:
            json.dump({"format": "csv", "params": {}}, f)
        with pytest.raises(ValueError, match="缺少 type 字段"):
            load_dir(d)
