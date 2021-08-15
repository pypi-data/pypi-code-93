"""This is the installation toolset for this project."""
from setuptools import setup, find_packages

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setup(name='MyCryptoKeys',
      version='0.1.0',
      author='alvaroperis',
      description='A Python MyCryptoKeys',
      long_description=long_description,
      packages=find_packages(exclude=('tests',)),
      entry_points={
          'console_scripts': [
              'MyCryptoKeys = MyCryptoKeys.__main__:main'
          ]
      })
