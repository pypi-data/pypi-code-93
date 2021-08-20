import os
from setuptools import  setup,find_packages

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT_DIR)

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='persianBrokers',
      version='0.2.2',
      description='description',
      author='M.Mortaz,M.Moalaghi',
      author_email='hdhshd@dd.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=find_packages(),
      install_requires=['requests']
     )
     