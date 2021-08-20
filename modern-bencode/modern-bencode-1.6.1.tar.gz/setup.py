"""Setup file, used for building a Python package."""
from setuptools import setup

with open("README.md", "r") as desc_file:
    long_description = desc_file.read()

setup(
    description="A simple bencode library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="modern-bencode",
    packages=["bencode"],
    package_data={"bencode": ["py.typed"]},
    python_requires=">=3.7",
    setup_requires=["setuptools_scm"],
    url="https://github.com/retonato/modern-bencode",
    use_scm_version=True,
)
