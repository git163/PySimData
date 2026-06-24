"""pysimdata - 仿真数据生成器"""
from .gaussian import GaussianGrid, GaussianBeam
from .function import (
    FunctionCurve,
    ErfCurve,
    TanhCurve,
    CoshCurve,
    ExponentialDecay,
    BilateralGaussian,
)

__all__ = [
    "GaussianGrid",
    "GaussianBeam",
    "FunctionCurve",
    "ErfCurve",
    "TanhCurve",
    "CoshCurve",
    "ExponentialDecay",
    "BilateralGaussian",
]

__version__ = "0.1.0"