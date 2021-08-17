import setuptools
from setuptools import version
from pathlib import Path

setuptools.setup(
    name="chandupdf",
    version=1.0,
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["tests","data"])
    
)