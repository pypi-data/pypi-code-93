import setuptools
from setuptools import setup
import idkwtfit


setup(
    name="idkwtfit",
    version=idkwtfit.__version__,
    author="ombe1229",
    author_email="h3236516@gmail.com",
    description="I don't know what the fuck is this",
    license="Apache 2.0",
    packages=setuptools.find_packages(),
    long_description=open("README.md").read(),
)
