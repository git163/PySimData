"""GaussianBeam: 高斯束斑"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pysimdata.function import GaussianBeam

gen = GaussianBeam(shape=(256, 256), sigma=20, amplitude=255, center=(128, 128))
data = gen.generate()
print(f"GaussianBeam: {data.shape}")
gen.save("output/gaussian_beam")