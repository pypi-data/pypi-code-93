import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="prayer_tool",
    version="2.1.1",
    description="The prayer assistant is a voice assistant that can tell when the next prayer will occur. The tool supports over 100 languages.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Nabil-Lahssini/prayer_assistant",
    author="Nabil Lahssini",
    author_email="NabilLahssini@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["prayer_tool"],
    install_requires=["gtts", "playsound", "googletrans==3.1.0a0", "requests"],
    entry_points={
        "console_scripts": ['prayer_tool=prayer_tool.__main__:main']
    },
)