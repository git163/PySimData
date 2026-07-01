"""2D 图像的 png/tiff 原始图片保存与加载测试"""
import json
import os
import tempfile

import numpy as np
import pytest

from pysimdata import GaussianBeam, load as load_dir


def test_save_load_tiff_lossless():
    """tiff 以 float32 无损保存，load 可回读且与原数据一致"""
    gen = GaussianBeam(shape=(16, 16))
    gen.generate()
    with tempfile.TemporaryDirectory() as d:
        out = gen.save_all(os.path.join(d, "b"), fmt="tiff")
        assert os.path.exists(os.path.join(out, "data.tiff"))
        with open(os.path.join(out, "config.json")) as f:
            cfg = json.load(f)
        assert cfg["format"] == "tiff"
        assert cfg["data_file"] == "data.tiff"
        loaded = load_dir(out)
    np.testing.assert_allclose(loaded.data, gen.data, atol=1e-4)


def test_save_load_png_uint8():
    """png 以 uint8 保存，load 回读与原数据的 uint8 量化一致"""
    gen = GaussianBeam(shape=(16, 16))
    gen.generate()
    with tempfile.TemporaryDirectory() as d:
        out = gen.save_all(os.path.join(d, "b"), fmt="png")
        assert os.path.exists(os.path.join(out, "data.png"))
        with open(os.path.join(out, "config.json")) as f:
            cfg = json.load(f)
        assert cfg["format"] == "png"
        assert cfg["data_file"] == "data.png"
        loaded = load_dir(out)
    np.testing.assert_array_equal(loaded.data, gen.data.astype(np.uint8))


def test_image_format_requires_2d():
    """png/tiff 仅支持 2D 数据，非 2D 抛 ValueError"""
    gen = GaussianBeam(shape=(16, 16))
    gen.generate()
    gen._data = np.zeros((4, 4, 3))  # 伪造非 2D 数据
    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(ValueError, match="仅支持 2D"):
            gen._save_data(d, "x", fmt="png")
