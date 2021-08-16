#!/usr/bin/env python
# coding: utf-8

"""The script supports publishing the YACF package to PyPI.

Instructions to release a new version of YACF:

(1) Prepare the release

* Write and test the code.
* Manually change the version number in __init__.py
* Call:

    $ python setup.py prepare


(2) Push to PyPI

This step releases the new version to PyPI.
Make sure your credentials are in pypirc.

* Call:

    $ python setup.py publish


(3) Post work

* Update information on the project home page

"""

# standard lib
import os
import setuptools
import sys

# first party
import yacf

FILE_ENCODING = "utf-8"

README_PATH = "README.md"
LICENSE_PATH = "LICENSE"

CLASSIFIERS = [
    # 3- alpha, 4 - beta, 5 - production/stable
    "Development Status :: 5 - Production/Stable",
    # Audience
    "Intended Audience :: Developers",
    # License
    "License :: OSI Approved :: MIT License",
    # Supported versions
    "Programming Language :: Python :: 3.7",
]


def _read(path: str) -> str:
    """Reads a text file and returns the content as unicode string.
    :param path: File path
    :return: content
    """
    with open(path, "rb") as f:
        b = f.read()
    return b.decode(FILE_ENCODING)


def _write(content: str, path: str):
    """Writes some content to a file
    :param content: Content of the new file
    :param path: File path
    """
    with open(path, "wb") as f:
        b = content.encode(FILE_ENCODING)
        f.write(b)


def _build_long_descr() -> str:
    """Build the long description
    :return: long description
    """
    readme = yacf.__doc__
    license = """\
# License

""" + _read(
        LICENSE_PATH
    )

    description = "\n\n".join([readme, license])

    return description


def prepare():
    """Prepares the process of publishing the new package."""
    # Write long description to README_PATH
    descr = _build_long_descr()
    _write(descr, README_PATH)


def publish():
    """Automates the process of publishing the new package."""

    if os.path.isdir("./dist"):
        os.system("rm -R ./dist")
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")


#
#
# Setup content
#
#


INSTALL_REQUIRES = ["toml"]
PACKAGES = setuptools.find_packages()


def main(args):
    command = args[-1]

    if command == "publish":
        publish()
        sys.exit()
    elif command == "prepare":
        prepare()
        sys.exit()

    version = yacf.version()
    descr = _read(README_PATH)

    setuptools.setup(
        name="yacf",
        version=version,
        license="MIT",
        description="Yet another configuration framework - Lightweight, easy to use.",
        long_description=descr,
        long_description_content_type="text/markdown",
        keywords="configuration config toml json",
        author="Max Resing",
        author_email="max.resing@protonmail.com",
        maintainer="Max Resing",
        maintainer_email="max.resing@protonmail.com",
        url="https://github.com/resingm/yacf",
        python_requires=">=3.7",
        install_requires=INSTALL_REQUIRES,
        packages=PACKAGES,
        classifiers=CLASSIFIERS,
        project_urls={
            "Source": "https://github.com/resingm/yacf",
            "Tracker": "https://github.com/resingm/yacf/issues",
        },
    )


if __name__ == "__main__":
    main(sys.argv)
