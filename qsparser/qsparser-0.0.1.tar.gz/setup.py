"""setup.py"""
import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='qsparser',
    version='0.0.1',
    description=('The query string parser for Python.'),
    long_description=README,
    long_description_content_type='text/markdown',
    author='Fillmula Inc.',
    author_email='victor.teo@fillmula.com',
    license='MIT',
    packages=find_packages(exclude=('tests')),
    package_data={'qsparser': ['py.typed']},
    zip_safe=False,
    url='https://github.com/fillmula/qsparser',
    include_package_data=True,
    python_requires='>=3.9')
