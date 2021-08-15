import pathlib
from setuptools import setup, find_packages
HERE = pathlib.Path(__file__).parent
VERSION = '0.0.0.1'
PACKAGE_NAME = 'findlcm'
AUTHOR = 'james'
AUTHOR_EMAIL = 'james@sandy.com'
URL = 'https://github.com/jamessandy/lcmfinder'
LICENSE = 'MIT'
DESCRIPTION = 'A package that helps find Lowest common multiple of a number'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"
# INSTALL_REQUIRES = [
#       'numpy',
#       'opencv'
# ]
setup(name="MyCustomPackage",
      #install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )