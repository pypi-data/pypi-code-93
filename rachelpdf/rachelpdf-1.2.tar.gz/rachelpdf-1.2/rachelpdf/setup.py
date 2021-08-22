import setuptools
from pathlib import Path


setuptools.setup(
    name="rachelpdf",
    version=1.2,
    long_description=Path("rachelpdf/README.md").read_text(),
    packages=setuptools.find_packages("rachelpdf",exclude=["tests","data"]))