from setuptools import setup

# setuptools comes as default package with pip

# the setup function is used to provide the package configuration

# name: pip install {name}, not necessarily the name of the code
# version: 0.0.x it means that is unstable
# description: one-liner
# py_modules: list of actual python modules to include
# package_dir: it tell setuptools that the code is under src

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='helloworld_disw',
    version='0.0.1',
    description='Say hello!',
    py_modules=["helloworld"],
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lautarodc",
    author="Lautaro Delgado",
    author_email="ldc0295@gmail.com",
    install_requires=[
        "blessings ~= 1.7",
    ],

    extras_require={
        "dev": [
            "pytest >= 3.7",
            "check-manifest",
            "twine",
        ],
    },
)
