import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
else:
    version = "0.0.3"

setuptools.setup(
    name="abbreviator",
    version=version,
    author="Willem Hendriks & Stephanie Wagenaar",
    author_email="whendrik@gmail.com",
    description="Abbreviate Long Sentences/Names based on hyphenation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BOLD-lab/abbreviator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['pyphen>=0.11.0']
)
