from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.2'
DESCRIPTION = 'Make a Server and client with socket.'


# Setting up
setup(
    name="serverclient",
    version=VERSION,
    author="S.B.Subbu Rakesh (India)",
    author_email="thevastofficial@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'Server', 'Client', 'socket server', 'socket Client', 'sockets'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
