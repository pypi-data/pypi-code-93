"""Setup for Crownstone Cloud library."""
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='crownstone-cloud',
    version="1.4.7",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/crownstone/crownstone-lib-python-cloud',
    author='Crownstone B.V.',
    packages=find_packages(exclude=['examples', 'tests']),
    install_requires=list(package.strip() for package in open('requirements.txt')),
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    python_requires='>=3.8',
)
