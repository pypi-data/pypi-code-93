import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="ASCII_art_tool",
    version="1.0.0",
    description="The ASCII art tool is a simple library to generate ASCII art from regular images.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Nabil-Lahssini/ASCII_art_tool",
    author="Nabil Lahssini",
    author_email="NabilLahssini@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["ascii_generator"],
    install_requires=[],
)