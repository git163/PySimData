"""BaseGenerator 测试"""
import numpy as np
import pytest
from pysimdata.base import BaseGenerator


def test_base_generator_requires_func_or_data_source():
    """必须提供 func 或 data_source"""
    with pytest.raises(ValueError, match="必须提供 func 或 data_source"):
        BaseGenerator()


def test_base_generator_with_func():
    """使用 func 生成数据"""
    def mock_func(x, y):
        return np.array([[x, y]])

    gen = BaseGenerator(func=mock_func, x=1, y=2)
    result = gen.generate()
    assert result.shape == (1, 2)


def test_base_generator_data_property():
    """data 属性返回生成的数据"""
    def mock_func(value):
        return np.array([[value]])

    gen = BaseGenerator(func=mock_func, value=42)
    gen.generate()
    assert gen.data[0, 0] == 42


def test_base_generator_data_property_before_generate():
    """generate 前访问 data 应抛出异常"""
    def mock_func():
        return np.array([[1]])

    gen = BaseGenerator(func=mock_func)
    with pytest.raises(ValueError, match="请先调用 generate"):
        _ = gen.data