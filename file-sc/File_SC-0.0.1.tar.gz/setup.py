from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.1'
DESCRIPTION = 'Simple File Transfer With sockets.'
LONGDESCRIPTION = 'you can find the project on github: https://github.com/programmingrakesh'



# Setting up
setup(
    name="File_SC",
    version=VERSION,
    author="S.B.Subbu Rakesh (India)",
    author_email="thevastofficial@gmail.com",
    description=DESCRIPTION,
    long_description = LONGDESCRIPTION,
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
