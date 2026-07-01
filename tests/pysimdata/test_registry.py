"""生成器注册表测试"""
import pytest

from pysimdata.base import BaseGenerator
from pysimdata.function import GaussianGrid, ErfCurve


def test_subclasses_auto_registered():
    """子类定义时自动登记到注册表"""
    assert BaseGenerator.get_generator_class("GaussianGrid") is GaussianGrid
    assert BaseGenerator.get_generator_class("ErfCurve") is ErfCurve


def test_unknown_type_raises():
    """未知 type 抛 ValueError 并提示可用类型"""
    with pytest.raises(ValueError, match="未注册的生成器类型"):
        BaseGenerator.get_generator_class("NotExist")
