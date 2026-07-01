"""load 与多格式读取测试"""
import json
import os
import tempfile

import numpy as np
import pytest

from pysimdata import FunctionCurve
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
