from setuptools import setup, find_packages

# read the contents of README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='NEMO_transaction_validation',
    version='0.2.11',
    packages=find_packages(),
    include_package_data=True,
    description='NEMO Plugin - Transaction Validation',
    long_description=long_description,
    long_description_content_type='text/markdown'
)