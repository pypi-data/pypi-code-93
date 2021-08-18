"""
This script is used to install uhepplot and all its dependencies. Run

    python setup.py install
or
    python3 setup.py install

to install the package.
"""

# Copyright (C) 2020-2021 Frank Sauerburger

from setuptools import setup

def load_long_description(filename):
    """
    Loads the given file and returns its content.
    """
    with open(filename) as readme_file:
        content = readme_file.read()
        return content

setup(name='uhepp',
      version='0.3.0',  # Also change in module and docs
      packages=["uhepp", "uhepp.tests"],
      install_requires=["tzlocal",
                        "requests",
                        "numpy",
                        "matplotlib",
                        "atlasify",
                        "pyyaml",
                        "python-dateutil"],  # Also add in requirements.txt
      test_suite='uhepp.tests',
      scripts=['bin/uhepp'],
      description='Universal HEP plots',
      long_description=load_long_description("README.md"),
      long_description_content_type='text/markdown',
      url="https://gitlab.cern.ch/fsauerbu/uhepp",
      author="Frank Sauerburger",
      author_email="f.sauerburger@cern.ch",
      classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: Physics",
      ],
      license="MIT")
