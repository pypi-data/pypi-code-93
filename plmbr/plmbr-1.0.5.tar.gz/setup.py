import setuptools
from plmbr.version import version

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="plmbr",
    version=version,
    author="Gilad Kutiel",
    author_email="gilad.kutiel@gmail.com",
    description="Reuseable Pipes",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://plmbr.github.io/plmbr/",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    install_requires=['tqdm']
)
