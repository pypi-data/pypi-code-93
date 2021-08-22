#!/usr/bin/env python3
import os

from setuptools import find_packages, setup

def exec_file(path_segments):
  result = {}
  code = read_file(path_segments)
  exec(code, result)
  return result

def read_file(path_segments):
  file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), *path_segments)
  with open(file_path) as f:
    return f.read()

version = exec_file(("rudy", "__init__.py"))["__version__"]
long_description = read_file(("README.md",))

setup(
  name="rudy",
  version=version,
  url="https://git.sr.ht/~jrb/rudy",
  description="a really stupid matrix bot",
  packages=find_packages(exclude=["tests", "tests.*"]),
  install_requires=[
    "matrix-nio[e2e]>=0.10.0",
  ],
  classifiers=[
    "License :: OSI Approved :: The Unlicense (Unlicense)",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
  ],
  long_description=long_description,
  long_description_content_type="text/markdown",

  scripts=["bin/rudy"],
)
