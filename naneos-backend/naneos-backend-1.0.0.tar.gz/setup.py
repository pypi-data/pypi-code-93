# -*- coding: utf-8 -*-
import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "PiPy_README.md").read_text()


setup(
    name="naneos-backend",
    version="1.0.0",
    description="Python Toolkit backend for communication with naneos and 3rd party devices.",
    long_description=README,
    long_description_content_type="text/markdown",
    author="huegi",
    author_email="mario.huegi@naneos.ch",
    url="https://github.com/naneos-org/python-naneos-backend",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    packages=find_packages(exclude=("tests", "docs")),
    # include_package_data=True,
    # package_data={"": ["data/batteries_metadata/*.json", "data/batteries_eec/*.pkl"]},
    # zip_safe=False,
    install_requires=["pyserial", "numpy", "pandas", "influxdb-client"],
)
