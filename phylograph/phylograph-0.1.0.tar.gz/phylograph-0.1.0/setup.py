from setuptools import setup, find_packages

setup(
    name='phylograph',
    version='0.1.0',
    packages=find_packages(),
    description='PhyloGraph is a python package for plotting evolutionary trees and data.',
    keywords = ['biology', 'evolution', 'phylogenetics', 'phylodynamics', 'comparative methods'],
    install_requires=[
        'pandas>=1.2.3',
        ],
    )