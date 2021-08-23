""" See [1] on how to write proper `setup.py` script.

[1] https://github.com/pypa/sampleproject/blob/master/setup.py
"""
import pathlib
import re

import setuptools


def version():
    here = pathlib.Path(__file__).parent.resolve()
    with open(here / "tutti_language_detector" / "__init__.py", "r") as f:
        for line in f:
            if re.match("^__version__ = ", line):
                version_string = re.search(r"[0-9]+\.[0-9]+\.[0-9]+", line).group(0).strip()
                return version_string


def requirements():
    """Extract requirements from `requirements.txt`"""
    here = pathlib.Path(__file__).parent.resolve()
    with open(here / "requirements.txt", "r") as f:
        reqs = [line.strip() for line in f if not re.match("^#", line)]
    return reqs


setuptools.setup(
    name="tutti_language_detector",
    version=version(),
    description="A tutti specific language detector.",
    long_description="A pre-trained language detection model for tutti.ch ads.",
    author="Oscar Saleta",
    author_email="oscar@tutti.ch",
    license="Proprietary",
    keywords=["language", "detector"],
    packages=setuptools.find_packages(exclude=["contrib", "docs", "*test*", "develop_new_model"]),
    python_requires=">=3.5.2",
    install_requires=requirements(),
    zip_safe=True,
    classifiers=["Programming Language :: Python :: 3", "Operating System :: OS Independent"],
    package_data={"tutti_language_detector": ["models/vw-0.0.1.model", "models/vw-0.0.2.model"]},
    include_package_data=True,
)
