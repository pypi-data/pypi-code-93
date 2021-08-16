#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pipenv install twine --dev

import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

# Package meta-data.
NAME = 'merc-common'
VERSION = None
DESCRIPTION = 'CRAMS API opensource merc-common package.'
URL = 'https://github.com/CRAMS-Dashboard/crams-api'
AUTHOR = 'Monash University e-Research Centre'
EMAIL = 'crams@monash.edu'

REQUIRES_PYTHON = '>=3.8.0'

# What packages are required for this module to be executed?
REQUIRED = [
    'Django>=3.2',
    'djangorestframework>=3.12',
    'django-rest-auth>=0.9.5',
    'django-cors-headers>=3.7.0',
    'django-extensions>=3.1.3',
    'django-filter>=2.4.0',
    'django-model-utils>=4.1.1',
    'mysqlclient>=2.0.3',
    'rest_condition>=1.0.3',
    'gunicorn>=20.0.4',
    'urllib3>=1.26.5',
    'sqlparse>=0.4.1',
    'pandas>=1.2.3',
    'PyJWT>=1.7.1',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# get the current directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(current_dir, 'README.rst'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(current_dir, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


class DistributeSource(Command):
    """ python setup.py dist."""

    description = 'Build the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous build dir ...')
            rmtree(os.path.join(current_dir, 'build'))

            self.status('Removing previous dist dir ...')
            rmtree(os.path.join(current_dir, 'dist'))
        except OSError:
            pass
        self.status('Building Source and Wheel (universal) distribution ...')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))
        sys.exit()


class PublishDist(Command):
    """Support setup.py upload."""

    description = 'Publish the package.'
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.status('Uploading the package to PyPI via Twine ...')
        os.system('twine upload dist/*')
        #
        # self.status('Pushing git tags…')
        # os.system('git tag v{0}'.format(about['__version__']))
        # os.system('git push --tags')
        sys.exit()


# Where the magic happens:
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),

    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },

    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='GNU General Public License v3.0',
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django :: 3.2',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    # $ setup.py build
    cmdclass={
        'dist': DistributeSource,
        'publish': PublishDist,
    },
)
