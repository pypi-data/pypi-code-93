#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Original solution from
#
#      https://github.com/navdeep-G/setup.py
#
#  Original license notice:
#
#  Copyright 2020 navdeep-G & GitHub contributors
#
#  Permission is hereby granted, free of charge, to any
#  person obtaining a copy of this software and associated
#  documentation files (the "Software"), to deal in the
#  Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute,
#  sublicense, and/or sell copies of the Software, and to
#  permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall
#  be included in all copies or substantial portions of the Software.

#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

#  NOTE: To use the 'upload' functionality of this file, you must:
#    $ pip install twine

import os
from pathlib import Path
from shutil import rmtree
import sys

from setuptools import Command, find_packages, setup
from setuptools.command.install import install

from grid.cli.utilities import check_environment_variables, GCPStorage, install_autocomplete
from grid.metadata import __package_name__, __version__

#   Package meta-data.
NAME = 'grid'
PACKAGE_NAME = __package_name__
DESCRIPTION = 'Grid Python SDK.'
URL = 'https://grid.ai'
EMAIL = 'grid-eng@grid.ai'
AUTHOR = 'Grid AI Engineering'
REQUIRES_PYTHON = '>=3.7.0'
VERSION = os.getenv("VERSION", __version__)

#  What packages are required for this module to be executed?
REQUIRED = []
with open('requirements.txt') as f:
    for line in f.readlines():
        REQUIRED.append(line.replace('\n', ''))

SETUP_REQUIRES = [
    'setuptools>=40.0',
    'wheel>=0.30',
]

#  What packages are optional?
EXTRAS = {}

#  The rest you shouldn't have to touch too much :)
#  ------------------------------------------------
#  Except, perhaps the License and Trove Classifiers!
#  If you do change the License, remember to
#  the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

#  Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


def upload_gcp_wheel(gcp_storage, version, bucket_name, blob_path):
    """
    Uploads lightning wheel to it's designated GCP bucket.
    """
    whl_exists = False
    for file in os.listdir('dist'):
        if '.whl' in file:
            wheel = file
            whl_exists = True

    if whl_exists:
        lastest_path = Path(blob_path) / "latest" / wheel
        version_path = Path(blob_path) / version / wheel

        # delete existing object in "latest" directory
        gcp_storage.delete_blobs(bucket_name=bucket_name, prefix=f'{blob_path}/latest/')

        gcp_storage.upload_blob(
            bucket_name=bucket_name, source_file_name=f'dist/{wheel}', destination_blob_name=lastest_path
        )
        gcp_storage.upload_blob(
            bucket_name=bucket_name, source_file_name=f'dist/{wheel}', destination_blob_name=version_path
        )
    else:
        raise ValueError("You did not build a wheel for this project.")


class UploadCommandPyPi(Command):
    """Support setup.py upload-pypi."""

    description = 'Build and publish the package.'
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
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        # skipcq: BAN-B605
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading the package to PyPI via Twine…')
        # skipcq: BAN-B605
        os.system('twine upload dist/*')

        sys.exit()


class UploadCommandGCP(Command):
    """Support setup.py upload-gcp."""

    description = 'Build and publish the package to GCP.'
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
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Checking environment variables…')
        check_environment_variables(['GOOGLE_APPLICATION_CREDENTIALS', 'GCP_GRID_BUCKET', 'GCP_BLOB_PATH'])

        self.status('Building Source and Wheel (universal) distribution…')
        # skipcq: BAN-B605
        os.system('{0} setup.py sdist bdist_wheel'.format(sys.executable))

        self.status('Uploading to GCP…')
        gcp_storage = GCPStorage()
        upload_gcp_wheel(
            gcp_storage=gcp_storage,
            version=VERSION,
            bucket_name=os.getenv('GCP_GRID_BUCKET'),
            blob_path=os.getenv('GCP_BLOB_PATH')
        )

        sys.exit()


class Install(install):
    """
    Override setup tools `install` command to do any pre/post install logic.
    """
    def run(self):
        install.run(self)
        install_autocomplete()


#  Where the magic happens:
setup(
    name=PACKAGE_NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    setup_requires=SETUP_REQUIRES,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests', 'tests.*')),
    entry_points={
        'console_scripts': ['grid=grid.cli.__main__:main'],
    },
    long_description="Grid AI Command Line Interface",
    long_description_content_type="text/x-rst",
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    #  $ setup.py publish support.
    cmdclass={
        'pypi': UploadCommandPyPi,
        'gcp': UploadCommandGCP,
        'install': Install
    },
)
