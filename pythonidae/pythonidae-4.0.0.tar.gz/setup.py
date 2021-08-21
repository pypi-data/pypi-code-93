
from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

DESCRIPTION = 'Fast, minimalist web framework for Python'

# Setting up
setup(
    name="pythonidae",
    version="4.0.0",
    author="parthka, sai, thehelkaproject",
    author_email="parthka.2005@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['jinja2'],
    keywords=['python', 'pythonidae', 'website', 'web framework', 'http'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
