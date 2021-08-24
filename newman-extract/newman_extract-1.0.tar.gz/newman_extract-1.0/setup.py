import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    setup(
    name="newman_extract",  # 专 辑
    version="1.0",  # current version
    author = "NewmanZhou",  # authors
    author_email = "fazhuolanyi@163.com",  # author_email
    description ="a very NB package", # Module introduction
    long_description = long_description,
    # long_description_content_type = "text/marklown",
    # url = "https://github.com/NewmanZhou/newman_extract.git",
    Packages =setuptools.find_packages (), # automatically find imported modules in the project
# Module related metadata (more description)
    classifiers = [
    "Programming Language :: Python :: 3",
    # "License:: OSI Approved:: MIT License",
    # "Operating System :: os Independent",
    ],
# dependency module
    install_requires=['pilLow'],

    python_requires = '>=3',)
