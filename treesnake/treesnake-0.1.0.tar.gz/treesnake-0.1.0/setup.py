from setuptools import setup, find_packages

setup(
    name='treesnake',
    version='0.1.0',
    packages=find_packages(),
    description='TreeSnake is a python package for inferring evolutionary trees',
    keywords = ['biology', 'evolution', 'phylogenetics'],
    install_requires=[
        'pandas>=1.2.3',
        ],
    )