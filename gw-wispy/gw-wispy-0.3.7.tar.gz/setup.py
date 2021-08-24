import setuptools

import codecs
import os.path

# versioning handled by the first method on:
# https://packaging.python.org/guides/single-sourcing-package-version/


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gw-wispy",
    version=get_version("wispy/__init__.py"),
    author="Sebastian Khan",
    author_email="KhanS22@Cardiff.ac.uk",
    description="Neural Network Based Waveform Modelling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/SpaceTimeKhantinuum/wispy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
    scripts=[
        "bin/wispy_generate_training_data",
        "bin/wispy_autoencoder_fit",
        "bin/wispy_make_explorer_workflow",
        "bin/wispy_plot_metrics",
    ],
)
