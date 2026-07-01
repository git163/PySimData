"""BilateralGaussian: 双边高斯"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import BilateralGaussian

gen = BilateralGaussian(shape=(128, 128), sigma=10, amplitude=255)
data = gen.generate()
print(f"BilateralGaussian: {data.shape}")
gen.save_all("output/bilateral_gaussian")