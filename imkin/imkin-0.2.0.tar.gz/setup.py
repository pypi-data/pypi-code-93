#!/usr/bin/env python3
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imkin",
    version="0.2.0",
    author="shllw",
    author_email="shllw@yahoo.com",
    description="Lightweight a movie and TV series data parser from imdb.com and kinopoisk.ru",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="parser imdb kinopoisk",
    url="https://bitbucket.org/shllw/imkin/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
)
