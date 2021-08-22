from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'Wrapper To Control NZX Virtual Trader'
LONG_DESCRIPTION = 'A package that allows easy access to information to place orders in the nzx virtual trading'

# Setting up
setup(
    name="nzx-virtual-trading",
    version=VERSION,
    author="Harry Ludemann",
    author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['selenium'],
    keywords=['nzx virtual trading', 'harryludemann', 'nzx virtual', 'virtual trading', 'nzx'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        # "Operating System :: Unix",
        # "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)