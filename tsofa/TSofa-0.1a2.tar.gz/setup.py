# Standard library imports.
import os

# Setuptools package imports.
from setuptools import setup

# Read the README.rst file for the 'long_description' argument given
# to the setup function.
README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# Allow setup.py to be run from any path.
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name = 'TSofa',
    version = '0.1a2',
    packages = ['tsofa', 'tsofa._views'],
    entry_points = {'console_scripts': [
        'tsofa-dsec-prd = tsofa._views._dsec_prd:main',
        'tsofa-dsec-pred = tsofa._views._dsec_pred:main',
        'tsofa-psec-pad = tsofa._views._psec_pad:main']},
    install_requires = [
        'pytz >= 2020.4', 'requests <= 2.22.0', 'Two-Percent >= 3.1'],
    license = 'BSD License',
    description = 'This package contains the reference CouchDB views for '\
        + 'well formatted timeseries data, the Python functionality to '\
        + 'retrieve data from those views, and functionality to process '\
        + 'the output.',
    long_description = README,
    url = 'https://bitbucket.org/notequal/tsofa/',
    author = 'Stanley Engle',
    author_email = 'stan.engle@gmail.com',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'],)

