import os
import inspect
from setuptools import setup
from mcconv.version import version as ejpm_version

# The directory containing this file
this_script_dir = os.path.dirname(inspect.stack()[0][1])

# The text of the README file
with open(os.path.join(this_script_dir, "pip_readme.md"), 'r') as readme_file:
    readme = readme_file.read()

# This call to setup() does all the work
setup(
    name="mcconv",
    version=ejpm_version,
    description="EIC Monte-Carlo file converter",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://eicweb.phy.anl.gov/monte_carlo/mcconv",
    author="Dmitry Romanov",
    author_email="romanov@jlab.org",
    license="MIT",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        "License :: OSI Approved :: MIT License",
        #"Programming Language :: Python :: 2",
        #"Programming Language :: Python :: 2.7",
        #"Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=["mcconv"],
    include_package_data=True,
    setup_requires=["click", "HepMC3", "uproot>=4", "awkward", "numpy"],
    install_requires=["click", "HepMC3", "uproot>=4", "awkward", "numpy"],
    entry_points={
        "console_scripts": [
            "eic2hepmc=mcconv:hepmc_convert_cli",
            "mcconv=mcconv:hepmc_convert_cli",
        ]
    },
)