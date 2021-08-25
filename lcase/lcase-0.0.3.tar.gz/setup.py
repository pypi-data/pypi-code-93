from setuptools import setup, find_packages
import sys

if sys.version_info < (3, 6):
    sys.exit("Sorry, Python < 3.6 is not supported.")

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

import lcase
VERSION = lcase.__version__

setup(
    name='lcase',
    version=VERSION,
    author='Zhiyi Huang',
    description='Latent CAusal Structure Estimator Python Package',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'numpy',
        'pandas',
        'scipy',
        'networkx',
        'scikit-learn',
        'statsmodels',
    ],
    url='https://github.com/zhi-yi-huang/lcase',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)