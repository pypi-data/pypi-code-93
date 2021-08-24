from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

DISTNAME = 'oppy'
VERSION = '0.0.6'
PACKAGES = find_packages()
EXTENSIONS = []
DESCRIPTION = 'An optimization package in python'
LONG_DESCRIPTION = long_description
AUTHOR = 'AG Volkwein'
MAINTAINER_EMAIL = 'agvolkwein.oppy@uni-konstanz.de'
LICENSE = 'BSD-3'
URL = 'https://gitlab.inf.uni-konstanz.de/ag-volkwein/oppy'

setuptools_kwargs = {
    'zip_safe': False,
    'install_requires': ['numpy',
                         'scipy',
                         'matplotlib'],
    'scripts': [],
    'include_package_data': True
}

setup(name=DISTNAME,
      version=VERSION,
      packages=PACKAGES,
      ext_modules=EXTENSIONS,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      author=AUTHOR,
      maintainer_email=MAINTAINER_EMAIL,
      license=LICENSE,
      url=URL,
      **setuptools_kwargs)
