import setuptools
from pathlib import Path

setuptools.setup(
    name="rachelpdf",
    version=1.3,
    long_description=Path("rachelpdf/README.md").read_text(),
    packages=setuptools.find_packages("rachelpdf",exclude=["tests","data"]))