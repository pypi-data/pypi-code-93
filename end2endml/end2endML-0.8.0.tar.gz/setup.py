# using setuptools
from setuptools import setup, find_packages
import pathlib

# get the path of setup.py
here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

# setup
setup(
    name="end2endML",
    version="0.8.0",
    author="Yipeng Song",
    author_email="yipeng.song@hotmail.com",
    description="Automate data analysis pipelines for data analyst",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/YipengUva/end2endml_pkg",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="data analysis, machine learning, automation",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6, <4",
    install_requires=[
        "numpy>=1.19",
        "pandas>=1.1",
        "imbalanced-learn>=0.8.0",
        "scikit-learn>=0.24",
        "pandas-profiling>=2.9.0",
        "joblib>=1.0",
        "xgboost>=1.4",
        "optuna>=2.7",
    ],
    project_urls={
        "Bug Tracker": "https://gitlab.com/YipengUva/end2endml_pkg/issues",
    },
)
