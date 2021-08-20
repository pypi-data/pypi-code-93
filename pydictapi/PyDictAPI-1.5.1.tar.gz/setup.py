from setuptools import setuptools, find_packages
import io

classifiers = [
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
    ]

with io.open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setuptools.setup(
    name="PyDictAPI",
    version="1.5.1",
    author="Shawan Mandal",
    author_email="imshawan.dev049@gmail.com",
    description="An advanced Dictionary and Translator Module for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imshawan/PyDictAPI",
    packages=find_packages(),
    classifiers=classifiers,
    install_requires=[
        'bs4',
        'requests',
        'urllib3'
    ]
)