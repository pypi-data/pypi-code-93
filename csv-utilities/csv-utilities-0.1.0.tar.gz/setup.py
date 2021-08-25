import os
from setuptools import find_packages, setup


__version__ = '0.1.0'


PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
README_PATH = os.path.join(PROJECT_PATH, 'README.md')

with open(README_PATH, 'r') as f:
    README_TEXT = f.read()

setup(
    name='csv-utilities',
    author='Connor Wallace',
    author_email="wallaconno@gmail.com",
    version=__version__,
    packages=find_packages(),
    description='A simple, no-dependency Python CSV library.',
    long_description=README_TEXT,
    long_description_content_type="text/markdown",
    url="https://github.com/cowalla/CSVUtilities",
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ]
)
