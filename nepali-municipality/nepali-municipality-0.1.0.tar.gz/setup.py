import setuptools as setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nepali-municipality',
    version='0.1.0',  # Required
    description='Nepali  municipalities is a python package to get data about Nepali municipalities based on districts ',
    url='https://github.com/nawarazpokhrel/Nepali-Municipalites',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Navaraj Pokharel',
    author_email='navarajpokharel@outlook.com',
    packages=setuptools.find_packages(include=['src', 'scr.*']) ,   # package_data={'src': ['src/data.json']}, install_requires=[],
    include_package_data=True,

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['Nepali', 'nepali districts', 'nepali municipalities', 'navaraj pokharel', 'nepali states'],
    python_requires='>=3.6',

)
