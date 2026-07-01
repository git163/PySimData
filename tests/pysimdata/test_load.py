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
