""" setup for package generation """

from os import path
from builtins import open
from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name="weaviate-etl",
      version="0.0.15",
      description="A weaviate python data extract transform load module.",
      long_description=long_description,
      long_description_content_type='text/markdown',
      author="SeMI Technologies",
      author_email="hello@semi.technology",
      packages=["weaviate_etl", "weaviate_etl.classification", "weaviate_etl.data", "weaviate_etl.schema"],
      python_requires='>=3.6',
      install_requires=[
        "weaviate-client>=2.3.0",
        "PyYAML==5.3.1",
        "openpyxl==3.0.5"])
