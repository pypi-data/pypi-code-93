from setuptools import setup, find_packages
import codecs
import os

long_description = open("README.md", "r").read()

VERSION = '1.0.3'
DESCRIPTION = 'Motion bot list status api tool'
LONG_DESCRIPTION = 'A package that allowes you to interact with the motion botlist API'

# Setting up
setup(
    name="motionbotlist",
    version=VERSION,
    author="TechnicPepijn",
    author_email="<tech@motiondevelopment.top>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['python', 'discord', 'disocrd-botlist', 'discord-bots', 'bots', 'botlist', 'motion', 'motiondev', 'motiondevelopment', 'motionbotlist'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
