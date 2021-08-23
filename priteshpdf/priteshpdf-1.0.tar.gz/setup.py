import setuptools
from pathlib import Path
setuptools.setup(
    name="priteshpdf",
    version=1.0,
    description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=["hhh"])
)
