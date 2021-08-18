import setuptools
from distutils.command.build_py import build_py
import os
import json
        
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="multiSourceWordMaps",
    version="0.0.11",
    author="Ot Gabaldon Torrents",
    author_email="gabaldonot@gmail.com",
    description="Allows the user to list sources and compile word maps from those sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.thisiswhy.biz",
    project_urls={
        "Bug Tracker": "https://www.thisiswhy.biz",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires = [
        "pdfminer.six",
        "wordcloud",
        "bs4",
        "requests",
        "pytest",
        "pytest-cov"
    ],
    entry_points= {
        'console_scripts': [
            'map = multiSourceWordMaps.wordMapCreator:main'
        ]
    }
)