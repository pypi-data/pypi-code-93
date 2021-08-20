"""
Define the Python package.
"""
import codecs
import os.path
from setuptools import setup, find_packages  # type: ignore

# The next two functions will help us set the package version number
# This is an implementation of the first solution proposal on how to have a single version number
# from the Python documentation:
# https://packaging.python.org/guides/single-sourcing-package-version/


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_package_string(rel_path, variable_name):
    for line in read(rel_path).splitlines():
        if line.startswith(variable_name):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError(
        f"Unable to find the {variable_name} package definition string.")


# Dependencies:
with open("requirements.txt", "r") as f:
    required = f.read().splitlines()

init_path = "forecast_dataprep/__init__.py"
package_name = get_package_string(init_path, 'PACKAGE_NAME')
setup(
    name=package_name,
    version=get_package_string(init_path, '__version__'),
    description=package_name +
    ' Python package',  # OBS! This will be publicly visible on pypi.org
    packages=find_packages(),
    install_requires=required,
    extras_require={"dev": ["jupyterlab"]},
    author='Elvia')
