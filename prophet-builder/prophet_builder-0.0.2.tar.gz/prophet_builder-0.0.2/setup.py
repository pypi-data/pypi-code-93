import os
import site

import setuptools
from setuptools.dist import Distribution
from subprocess import call

MIN_PYTHON_VERSION = "3.7"
SETUP_REQUIRES = ["wheel"]

DISTNAME = "prophet_builder"
DESCRIPTION = "A package to set the environment variables for CMDSTANPY backend support and to install prophet," \
              " so it can be used as an extension to EvalML"
LICENSE = "BSD-3-Clause"
VERSION = "0.0.2"

class BinaryDistribution(Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(foo):
        return True

with open("README.md", "r") as fh:
    long_description = fh.read()


def setup_package():
    call('pip install cmdstan-builder', shell=True)

    metadata = dict(
        name=DISTNAME,
        description=DESCRIPTION,
        long_description=long_description,
        long_description_content_type="text/markdown",
        author='Alteryx, Inc.',
        author_email='support@featurelabs.com',
        license=LICENSE,
        version=VERSION,
        url='https://github.com/alteryx/cmdstan_ext/',
        python_requires=">={}".format(MIN_PYTHON_VERSION),
        setup_requires=SETUP_REQUIRES,
        install_requires=open("requirements.txt").readlines(),
        packages=setuptools.find_packages(),
        include_package_data=True,
        distclass=BinaryDistribution
    )

    from setuptools import setup
    setup(**metadata)

    os.environ["CMDSTAN"] = f"{site.getsitepackages()[0]}/cmdstan_builder/stan/cmdstan-2.27.0"
    os.environ["STAN_BACKEND"] = "CMDSTANPY"
    print(f'CMDSTAN location: {os.getenv("CMDSTAN")}')
    call('pip install prophet==1.0.1', shell=True)
    call('pip uninstall pystan -y', shell=True)
    print("PyStan uninstalled")


if __name__ == "__main__":
    setup_package()
