#modified from: https://towardsdatascience.com/deep-dive-create-and-publish-your-first-python-library-f7f618719e14 19/8/2021
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="SymFlow",
    version="0.1.0",
    description="Library for using SymPy expressions as Keras layers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://SymFlow.readthedocs.io/",
    author="Paul Spiering",
    author_email="paul@spiering.org",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=["symflow"],
    include_package_data=True,
    install_requires=["numpy","tensorflow","sympy"]
)
