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