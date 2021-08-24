import os.path
from setuptools import setup

HERE = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

setup(
    name="views_extraction",
    version="1.1.0",
    description="This project extracts the view data of every post from WordPress.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/AbhisarAnand/LPBI-Data-Extraction-Project",
    author="Abhisar Anand, Srinivas Sriram",
    author_email="abhisar.muz@gmail.com, srinivassriram06@gmail.com",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["views_extraction"],
    include_package_data=True,
    install_requires=[
        "Cython", "getpass4", "selenium", "pandas", "webdriver-manager", "numpy", "python-dateutil", "setuptools", "openpyxl", "tqdm", "psutil", "colorama"
    ],
    entry_points={"console_scripts": [
        "views_extraction=views_extraction.__main__:main"]},
)
