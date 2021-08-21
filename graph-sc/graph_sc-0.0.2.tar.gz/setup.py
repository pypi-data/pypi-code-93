import os

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read()

setup(
    name="graph_sc",
    author_email="ciortanmadalina@gmail.com",
    version="0.0.2",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[requirements],
    python_requires=">=3.6",
    description="Graph-sc",
    include_package_data=True,
    package_data={"": ["**/*.h5"]},
)
