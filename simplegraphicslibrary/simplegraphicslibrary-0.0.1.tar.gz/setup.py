from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Making some stuff simpler...'
LONG_DESCRIPTION = 'Did you EVER wanted a BETTER pygame?. Wellp, you will not find it!'

# Setting up
setup(
    name="simplegraphicslibrary",
    version=VERSION,
    author="FoctasticCode",
    author_email="youdont.have@to.know",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pygame'],
    keywords=['python', 'pygame', 'graphics'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)