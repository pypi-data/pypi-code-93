#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


readme = open('README.rst').read()

setup(
    name='serialbox',
    version='2.4.1',
    url='http://www.serial-lab.com',
    license='GPL',
    long_description=readme,
    description='Serial Number Distribution Made Easy.',
    author='SerialLab Corp',
    author_email='slab@serial-lab.com',
    packages=find_packages(),
    package_data=get_package_data('serialbox'),
    install_requires=['django', 'djangorestframework',
                      'djangorestframework-csv',
                      'djangorestframework-xml', 'Markdown', 'decorator',
                      'six',
                      'docutils'],
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
    ]
)
