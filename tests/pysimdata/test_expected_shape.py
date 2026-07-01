"""expected_shape 默认推导测试"""
from pysimdata.function import GaussianGrid, ErfCurve


def test_image_generator_shape_from_shape_param():
    """图像类从 shape 参数推导期望形状"""
    gen = GaussianGrid(shape=(128, 128), num_points=4)
    assert gen.expected_shape() == (128, 128)


def test_curve_generator_shape_from_yshape_numpoints():
    """曲线类从 y_shape + num_points 推导期望形状"""
    gen = ErfCurve(num_points=100, y_shape=50)
    assert gen.expected_shape() == (50, 100)
