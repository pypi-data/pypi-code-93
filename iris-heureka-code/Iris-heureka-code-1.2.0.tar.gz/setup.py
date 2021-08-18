import setuptools
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="Iris-heureka-code",
    version="1.2.0",
    author="heureka-code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    description="Eventbasierte Kommunikation",
    url="https://github.com/heureka-code/Iris-heureka-code",
    download_url="https://github.com/heureka-code/Iris-heureka-code/archive/refs/tags/1.2.0.tar.gz",
    packages=setuptools.find_packages()
    )
