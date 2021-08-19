#!/usr/bin/env python3
import os
import shutil

from setuptools import Command
from setuptools import setup

NAME = "pytest_pop"
DESC = "A pytest plugin to help with testing pop projects"

# Version info -- read without importing
VERSION = "8.0.1"

SETUP_DIRNAME = os.path.dirname(__file__)
if not SETUP_DIRNAME:
    SETUP_DIRNAME = os.getcwd()

with open("README.rst", encoding="utf-8") as f:
    LONG_DESC = f.read()

requires_found = None
if os.path.exists("requirements/base.txt"):
    requires_found = "requirements/base.txt"
else:
    # We are running from inside an sdist:
    egg_info_dir = os.path.join(os.path.dirname(__file__), f"{NAME}.egg-info")
    requires_txt = os.path.join(egg_info_dir, "requires.txt")
    if os.path.exists(requires_txt):
        requires_found = requires_txt

if requires_found:
    with open(requires_found) as f:
        REQUIREMENTS = f.read().splitlines()
else:
    REQUIREMENTS = []


class Clean(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        for subdir in (NAME, "tests"):
            for root, dirs, files in os.walk(
                os.path.join(os.path.dirname(__file__), subdir)
            ):
                for dir_ in dirs:
                    if dir_ == "__pycache__":
                        shutil.rmtree(os.path.join(root, dir_))


def discover_packages():
    modules = []
    # dot-delimited list of modules to not package. It's not good to package tests:
    skip_mods = ["tests"]
    for root, _, files in os.walk(os.path.join(SETUP_DIRNAME, NAME)):
        pdir = os.path.relpath(root, SETUP_DIRNAME)
        modname = pdir.replace(os.sep, ".")
        if modname not in skip_mods:
            modules.append(modname)
    return modules


setup(
    name="pytest-pop",
    author="Tyler Johnson",
    author_email="tjohnson@saltstack.com",
    url="https://gitlab.com/saltstack/pop/pytest-pop",
    version=VERSION,
    install_requires=REQUIREMENTS,
    description=DESC,
    long_description=LONG_DESC,
    long_description_content_type="text/x-rst",
    python_requires=">=3.6",
    classifiers=[
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 5 - Production/Stable",
    ],
    packages=discover_packages(),
    entry_points={"pytest11": ["pytest-pop = pytest_pop.plugin"]},
    cmdclass={"clean": Clean},
)
