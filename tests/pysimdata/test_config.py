"""配置加载/保存测试"""
import json
import os
import tempfile

import numpy as np
import pytest

from pysimdata.function import (
    GaussianGrid,
    GaussianBeam,
    FunctionCurve,
    ErfCurve,
    TanhCurve,
    CoshCurve,
    ExponentialDecay,
    BilateralGaussian,
)


class TestGaussianGridConfig:
    """GaussianGrid 配置测试"""

    def test_from_config_dict(self):
        """从字典加载配置"""
        config = {
            "type": "GaussianGrid",
            "params": {
                "shape": [64, 64],
                "mean": 0,
                "std": 1,
                "num_points": 3,
            },
        }
        gen = GaussianGrid.from_config(config)
        data = gen.generate()
        assert data.shape == (64, 64)

    def test_from_config_file(self):
        """从 JSON 文件加载配置"""
        config = {
            "type": "GaussianGrid",
            "params": {"shape": [32, 32], "num_points": 2},
        }
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(config, f)
            temp_path = f.name

        try:
            gen = GaussianGrid.from_config(temp_path)
            data = gen.generate()
            assert data.shape == (32, 32)
        finally:
            os.unlink(temp_path)

    def test_to_config(self):
        """导出配置"""
        gen = GaussianGrid(shape=(128, 128), mean=0, std=1, num_points=5, seed=42)
        config = gen.to_config()

        assert config["type"] == "GaussianGrid"
        assert config["params"]["shape"] == [128, 128]
        assert config["params"]["mean"] == 0
        assert config["params"]["std"] == 1
        assert config["params"]["num_points"] == 5

    def test_save_config(self):
        """保存配置到文件"""
        gen = GaussianGrid(shape=(64, 64), num_points=3)

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            gen.save_config(config_path)

            assert os.path.exists(config_path)

            with open(config_path) as f:
                loaded = json.load(f)
            assert loaded["type"] == "GaussianGrid"
            assert loaded["params"]["shape"] == [64, 64]

    def test_roundtrip(self):
        """创建 → 导出 → 导入 → 生成"""
        gen1 = GaussianGrid(shape=(64, 64), mean=0, std=1, num_points=3, seed=123)
        data1 = gen1.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            gen1.save_config(config_path)

            # 重新加载
            gen2 = GaussianGrid.from_config(config_path)
            data2 = gen2.generate()

        # 数据应相同 (相同 seed)
        np.testing.assert_array_almost_equal(data1, data2)


class TestGaussianBeamConfig:
    """GaussianBeam 配置测试"""

    def test_from_config_dict(self):
        """从字典加载配置"""
        config = {
            "type": "GaussianBeam",
            "params": {
                "shape": [128, 128],
                "sigma": 10,
                "amplitude": 200,
                "center": [64, 64],
            },
        }
        gen = GaussianBeam.from_config(config)
        data = gen.generate()
        assert data.shape == (128, 128)
        assert data[64, 64] == 200

    def test_to_config(self):
        """导出配置"""
        gen = GaussianBeam(shape=(256, 256), sigma=15, amplitude=255, center=(128, 128))
        config = gen.to_config()

        assert config["type"] == "GaussianBeam"
        assert config["params"]["shape"] == [256, 256]
        assert config["params"]["sigma"] == 15
        assert config["params"]["amplitude"] == 255

    def test_roundtrip(self):
        """创建 → 导出 → 导入 → 生成"""
        gen1 = GaussianBeam(shape=(64, 64), sigma=5, amplitude=255, center=(32, 32))
        data1 = gen1.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            gen1.save_config(config_path)

            gen2 = GaussianBeam.from_config(config_path)
            data2 = gen2.generate()

        np.testing.assert_array_almost_equal(data1, data2)


class TestFunctionCurveConfig:
    """FunctionCurve 配置测试"""

    def test_from_config_dict_sin(self):
        """从字典加载 sin 配置"""
        config = {
            "type": "FunctionCurve",
            "params": {
                "func": "sin",
                "x_range": [0, np.pi],
                "num_points": 50,
                "y_shape": 30,
            },
        }
        gen = FunctionCurve.from_config(config)
        data = gen.generate()
        assert data.shape == (30, 50)

    def test_from_config_dict_cos(self):
        """从字典加载 cos 配置"""
        config = {
            "type": "FunctionCurve",
            "params": {"func": "cos", "num_points": 40},
        }
        gen = FunctionCurve.from_config(config)
        data = gen.generate()
        assert data.shape == (100, 40)

    def test_to_config(self):
        """导出配置"""
        gen = FunctionCurve(func=np.cos, x_range=(0, np.pi), num_points=80, amplitude=2.0)
        config = gen.to_config()

        assert config["type"] == "FunctionCurve"
        assert config["params"]["func"] == "cos"
        assert config["params"]["num_points"] == 80
        assert config["params"]["amplitude"] == 2.0

    def test_roundtrip(self):
        """创建 → 导出 → 导入 → 生成"""
        gen1 = FunctionCurve(func=np.tan, x_range=(0, np.pi / 2), num_points=25, y_shape=20)
        data1 = gen1.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            gen1.save_config(config_path)

            gen2 = FunctionCurve.from_config(config_path)
            data2 = gen2.generate()

        np.testing.assert_array_almost_equal(data1, data2)


class TestErfCurveConfig:
    """ErfCurve 配置测试"""

    def test_from_config_dict(self):
        """从字典加载配置"""
        config = {
            "type": "ErfCurve",
            "params": {
                "x_range": [-2, 2],
                "num_points": 60,
                "y_shape": 40,
            },
        }
        gen = ErfCurve.from_config(config)
        data = gen.generate()
        assert data.shape == (40, 60)

    def test_to_config(self):
        """导出配置"""
        gen = ErfCurve(x_range=(-3, 3), num_points=50, amplitude=1.5)
        config = gen.to_config()

        assert config["type"] == "ErfCurve"
        assert config["params"]["x_range"] == [-3, 3]
        assert config["params"]["amplitude"] == 1.5

    def test_roundtrip(self):
        """创建 → 导出 → 导入 → 生成"""
        gen1 = ErfCurve(x_range=(-1, 1), num_points=30, y_shape=20)
        data1 = gen1.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            gen1.save_config(config_path)

            gen2 = ErfCurve.from_config(config_path)
            data2 = gen2.generate()

        np.testing.assert_array_almost_equal(data1, data2)


class TestExponentialDecayConfig:
    """ExponentialDecay 配置测试"""

    def test_from_config_dict(self):
        """从字典加载配置"""
        config = {
            "type": "ExponentialDecay",
            "params": {
                "shape": [64, 64],
                "tau": 15.0,
                "amplitude": 200,
                "direction": "y",
            },
        }
        gen = ExponentialDecay.from_config(config)
        data = gen.generate()
        assert data.shape == (64, 64)

    def test_to_config(self):
        """导出配置"""
        gen = ExponentialDecay(shape=(128, 128), tau=20.0, amplitude=255, direction="y")
        config = gen.to_config()

        assert config["type"] == "ExponentialDecay"
        assert config["params"]["shape"] == [128, 128]
        assert config["params"]["tau"] == 20.0
        assert config["params"]["direction"] == "y"

    def test_roundtrip(self):
        """创建 → 导出 → 导入 → 生成"""
        gen1 = ExponentialDecay(shape=(32, 32), tau=5.0, amplitude=100, direction="x")
        data1 = gen1.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            gen1.save_config(config_path)

            gen2 = ExponentialDecay.from_config(config_path)
            data2 = gen2.generate()

        np.testing.assert_array_almost_equal(data1, data2)


class TestBilateralGaussianConfig:
    """BilateralGaussian 配置测试"""

    def test_from_config_dict(self):
        """从字典加载配置"""
        config = {
            "type": "BilateralGaussian",
            "params": {
                "shape": [64, 64],
                "sigma": 8.0,
                "amplitude": 200,
                "center": [32, 32],
            },
        }
        gen = BilateralGaussian.from_config(config)
        data = gen.generate()
        assert data.shape == (64, 64)
        assert data[32, 32] == 200

    def test_to_config(self):
        """导出配置"""
        gen = BilateralGaussian(shape=(128, 128), sigma=12.0, amplitude=255)
        config = gen.to_config()

        assert config["type"] == "BilateralGaussian"
        assert config["params"]["shape"] == [128, 128]
        assert config["params"]["sigma"] == 12.0

    def test_roundtrip(self):
        """创建 → 导出 → 导入 → 生成"""
        gen1 = BilateralGaussian(shape=(32, 32), sigma=5.0, amplitude=255)
        data1 = gen1.generate()

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            gen1.save_config(config_path)

            gen2 = BilateralGaussian.from_config(config_path)
            data2 = gen2.generate()

        np.testing.assert_array_almost_equal(data1, data2)