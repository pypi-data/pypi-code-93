import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cm2metrics",
    version="0.1",
    author="Zhi Liu",
    author_email="cowliucn@gmail.com",
    description="A lightweight package that analyzes multiple metrics directly from confusion matrix efficiently",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FisherDock/m2metrics",
    packages=setuptools.find_packages(),
    install_requires=['pandas>=1.0'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)