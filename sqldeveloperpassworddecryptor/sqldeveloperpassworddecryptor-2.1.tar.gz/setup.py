#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='sqldeveloperpassworddecryptor',
      version='2.1',
      description='A simple script to decrypt stored passwords from the Oracle SQL Developer IDE',
      long_description=open('sqldeveloperpassworddecryptor/README.md').read(),
      long_description_content_type='text/markdown; charset=UTF-8;',
      url='https://github.com/maaaaz/sqldeveloperpassworddecryptor',
      author='Thomas D.',
      author_email='tdebize@mail.com',
      license='LGPL',
      classifiers=[
        'Topic :: Security',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
      ],
      keywords='oracle sqldeveloper password decryptor',
      packages=find_packages(),
      install_requires=['pycryptodomex'],
      python_requires='>=2.7',
      entry_points = {
        'console_scripts': ['sqldeveloperpassworddecryptor=sqldeveloperpassworddecryptor.sqldeveloperpassworddecryptor:main'],
      },
      include_package_data=True)