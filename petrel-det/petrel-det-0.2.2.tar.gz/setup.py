from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

exec(open("petrel/version.py").read())
setup(
    name="petrel-det",
    version=__version__,
    description="Code to streamline Pytorch EfficientDet applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DanielMorton/Petrel",
    author="Daniel Morton",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    # Note that this is a string of words separated by whitespace, not a list.
    packages=find_packages(exclude=["test"]),
    install_requires=["albumentations >= 1.0.3", "effdet >= 0.2.4",
                      "opencv_python >=4.5.2.54", "pandas >= 1.1.5", "torch >= 1.9"],
    python_requires=">=3.7",
)