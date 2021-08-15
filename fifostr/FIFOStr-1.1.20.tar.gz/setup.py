
"""
fifostr.py installer file for pip packager

setup file for pip install.
 
See:
    https://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/quickstart.html

taken from: 
    https://github.com/pypa/sampleproject

see runbuild.sh for packaging (yes its shell script but it has all the other steps in it.)

- m a chatterjee (c) 2012,2017,2018

"""
 
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path
 
#get the package version from ... the package
import sys
sys.path.append('./fifostr')  #this is just to find fifostr which is in one up in the dir 
from fifostr import *

def getFIFOStrVersion():
    f = FIFOStr()
    return f.ver()["version_str"]

here = path.abspath(path.dirname(__file__))
 
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
 
setup(
    name='FIFOStr',
 
    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=getFIFOStrVersion(),
 
    description='fifostr - A FIFO (first in first out) buffer for strings derived from deque with pattern match callbacks',
    long_description=long_description,
    long_description_content_type='text/markdown',

    # The project's main homepage.
    url='https://github.com/deftio/fifostr',
    download_url='https://pypi.python.org/pypi/fifostr',

    # Author details
    author='manu chatterjee',
    author_email='deftio@deftio.com',
 
    # Choose your license
    license='BSD License',
 
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
 
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        #'Topic :: Software Development ',
 
        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',
 
        # 
        'Programming Language :: Python :: 2',
        #'Programming Language :: Python :: 2.6', not tested on 2.6
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3', # travis CI no longer supports 3.3 but FIFOstr does and passes all tests
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
 

    # What does your project relate to?
    keywords='string stream parsing, parser utilities',
 
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    #packages=find_packages(exclude=['dev','docs', 'tests']),
    packages=['fifostr'],
    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #py_modules=["fifostr.fifostr"],
 
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    #install_requires=['collections'],
 
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test] 
    extras_require={
        'dev': ['check-manifest'],
        'test': ['pytest']
    },
 
    package_dir={'fifostr' : 'fifostr'},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #package_data={
    #   'sample': ['package_data.dat'],
    #},
 
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],
 
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    #entry_points={
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},
    test_suite = "py.test"
)