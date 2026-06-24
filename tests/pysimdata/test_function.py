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