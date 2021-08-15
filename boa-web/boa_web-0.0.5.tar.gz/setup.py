import pathlib
import setuptools
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent
# The text of the README file
README = (HERE / "README.md").read_text()
# save requirements in a list 
REQUIREMENTS = open('requirements.txt').read().splitlines()
# This call to setup() does all the work
setup(
    name="boa_web",
    version="0.0.5",
    description="boa_web is electron.js for python",
    keywords='flask, electron, eel, cefpython, html, css, javascript',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/atharva-naik/boa_web",
    author="Atharva Naik",
    author_email="atharvanaik2018@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=['boa_web'],
    include_package_data=True,
    install_requires=REQUIREMENTS,
)