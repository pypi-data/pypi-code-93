"""Setup script for package."""
# pylint: disable=consider-using-with

import re

from setuptools import find_packages, setup

match = re.search(
    r'^VERSION\s*=\s*"(.*)"',
    open("voight_kampff/version.py", encoding="utf_8").read(),
    re.M,
)

VERSION = match.group(1) if match else "???"
with open("README.md", "rb") as f:
    LONG_DESCRIPTION = f.read().decode("utf-8")

setup(
    name="voight-kampff",
    version=VERSION,
    description="Simple command line app for running Python linters.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author="Soren Kristiansen",
    author_email="soren@gutsandglory.dk",
    url="https://github.com/sorenlind/voight-kampff/",
    keywords="",
    packages=find_packages(),
    install_requires=[
        "bandit",
        "black",
        "flake8",
        "pydocstyle",
        "pylint",
        "pyenchant",
    ],
    extras_require={
        "dev": [
            "coverage",
            "rope",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "tox",
        ],
        "test": [
            "coverage",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "tox",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
    ],
    entry_points={
        "console_scripts": [
            "vk = voight_kampff.__main__:main",
        ]
    },
)
