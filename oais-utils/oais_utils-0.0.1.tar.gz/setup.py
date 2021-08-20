import pathlib
import os
import re
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# Get the version string. Cannot be done with import!
with open(os.path.join("oais_utils", "version.py"), "rt") as f:
    version = re.search(r'__version__\s*=\s*"(?P<version>.*)"\n', f.read()).group(
        "version"
    )

# This call to setup() does all the work
setup(
    name="oais_utils",
    version=version,
    description="OAIS utilities",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://gitlab.cern.ch/digitalmemory/utils",
    author="Antonio Vivace",
    author_email="antonio.vivace@cern.ch",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=find_packages(include=["oais_utils", "oais_utils.*"]),
    include_package_data=True,
    install_requires=[],
)
