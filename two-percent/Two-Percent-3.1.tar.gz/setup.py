# Standard library imports.
import os

# Setuptools package imports.
from setuptools import setup

# Read the README.rst file for the 'long_description' argument given
# to the setup function.
README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# Allow setup.py to be run from any path.
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name = 'Two-Percent',
    version = '3.1',
    packages = ['twopct'],
    license = 'BSD License',
    description = 'This package provides a very simple framework for '\
        + 'making command line python scripts.',
    long_description = README,
    url = 'https://bitbucket.org/notequal/two-percent/',
    author = 'Stanley Engle',
    author_email = 'stan.engle@gmail.com',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'],)

