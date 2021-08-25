"""
Setup dzy package
"""
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

setup(
    name="dzy",
    version="1.0.1",
    description="dzy Python package",
    author="dzy",
    packages=find_packages(where="dzy"),
    python_requires=">=3.6, <4",
    # install_requires=[""]
)
