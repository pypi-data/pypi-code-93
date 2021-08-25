import codecs
from setuptools import setup
from pathlib import Path

URGE_VERSION = "0.4.2"
DOWNLOAD_URL = ""


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [str(path.parent) for path in Path(package).glob("**/__init__.py")]


def read_file(filename):
    """
    Read a utf8 encoded text file and return its contents.
    """
    with codecs.open(filename, "r", "utf8") as f:
        return f.read()


setup(
    name="urge",
    packages=get_packages("urge"),
    version=URGE_VERSION,
    description="You've got the Urge to write some code ,so go ahead",
    long_description=read_file("README.md"),
    license="MIT",
    author="Hou",
    author_email="hhhoujue@gmail.com",
    url="",
    download_url=DOWNLOAD_URL,
    keywords=["schedule", "jobs", "toy", "file", "utils"],
    install_requires=[
        "playwright==1.13.0",
        "schedule==1.1.0",
        "pyquery",
        "daoism",
        "httpx",
        "path",
        "fs",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Natural Language :: English",
    ],
    python_requires=">=3.7",
)
