from setuptools import setup, find_packages
import codecs
import os


VERSION = '1.0'
DESCRIPTION = 'DB table export'
LONG_DESCRIPTION = 'DB table export'

# Setting up
setup(
    name="pydbexport",
    version=VERSION,
    author="Md. Imrul Hasan",
    author_email="imrulhasan273@gmail.com",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['sqlalchemy','pandas'],
    keywords=[''],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)