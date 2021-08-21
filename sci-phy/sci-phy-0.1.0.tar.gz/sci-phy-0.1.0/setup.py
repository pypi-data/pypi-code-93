from setuptools import setup, find_packages

setup(
    name='sci-phy',
    version='0.1.0',
    packages=find_packages(),
    description='Sci-Phy is a python package  for the statistical analysis and modelling of evolved data using phylogenetic trees (phylogenetic comparative methods)',
    keywords = ['biology', 'evolution', 'phylogenetics'],
    install_requires=[
        'pandas>=1.2.3',
        ],
    )