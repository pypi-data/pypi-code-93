
import setuptools
from bioutensil.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bioutensil",
    version=__version__,
    author="Lingxi Chen",
    author_email="chanlingxi@gmail.com",
    description="Bioinformatics utensil",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paprikachan/bioutensil",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
