import io
import os
import re

from setuptools import find_packages
from setuptools import setup

from dotenv import dotenv_values
env = dotenv_values('.env')

version = f'{env["major"]}.{env["minor"]}.{env["patch"]}'

with open("README.md", "r") as fh:
    long_description = fh.read()

def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())

setup(
    name="jh_utils",
    version=version,
    url='https://github.com/JohnHolz/jh_utils',
    license='MIT',

    author="joao holz",
    author_email="joaopaulo.paivaholz@gmail.com",

    description="Some simple functions to all projects",
    long_description=long_description,
    long_description_content_type='text/markdown',

    packages=find_packages(exclude=('tests',)),

    install_requires=[],

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
)
