import sys
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='Simperium3',
    version='0.1.5',
    author='Andy Gayton',
    author_email='andy@simperium.com',
    packages=['simperium', 'simperium.test'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.sr.ht/~swalladge/python-simperium3",
    description='Python 3 client for the Simperium synchronization platform',
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests'],
    python_requires='>=3',
)
