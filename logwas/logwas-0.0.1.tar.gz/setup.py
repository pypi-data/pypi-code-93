from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Jeu de stratégie sur plateau'
LONG_DESCRIPTION = 'Un packet vous permettant de jouer a un petit jeu de stratégie sur plateau'

# Setting up
setup(
    name="logwas",
    version=VERSION,
    author="Bouhdid Wassim",
    author_email="<mail.wassim@hotmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pygame'],
    keywords=['python', 'war', 'strategy', 'game','pygame'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)