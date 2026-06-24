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