import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name="parselcode",
    version="1.0.0",
    description="Substitution based Cipher to Encrypt/Decrypt by mapping word structure to hindu birth chart houses",
    long_description =long_description,
    long_description_content_type = "text/markdown",
    url="https://github.com/Puru-Malhotra/parselcode",
    author="Puru Malhotra",
    author_email="purumalhotra99@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["parselcode"],
    include_package_data=True,
    install_requires=["pandas"],
)
