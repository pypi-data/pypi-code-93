#*****************************************************************#
# (C) Copyright IBM Corporation 2020.                             #
#                                                                 #
# The source code for this program is not published or otherwise  #
# divested of its trade secrets, irrespective of what has been    #
# deposited with the U.S. Copyright Office.                       #
#*****************************************************************#

import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")) as f:
    long_description = f.read()

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "requirements.txt")) as f:
    requirements = f.readlines()

# Read version from the env
version = os.environ.get("RELEASE_VERSION")
assert version is not None, "Must set RELEASE_VERSION"

setup(
    name="alchemy-config",
    version=version,
    description="Configuration framework in Python for general configuration use.",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/IBM/alchemy-config",
    author="Gabe Goodhart",
    author_email="gabe.l.hart@gmail.com",
    license="MIT",
    keywords="config",
    packages=["aconfig"],
    install_requires=requirements,
)
