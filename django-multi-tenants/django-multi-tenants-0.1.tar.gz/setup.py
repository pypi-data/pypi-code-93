#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.1'

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='django-multi-tenants',
    version=VERSION,
    author='Cristian Restrepo',
    author_email='crstnrrm@gmail.com',
    packages=find_packages(),
    scripts=[],
    url='https://gitlab.com/crstnrm/django-multi-tenants',
    license='MIT',
    description='Multi tenant support for Django using PostgreSQL schemas.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries',
    ],
    install_requires=[
        'Django>=2.2.0',
        'django-tenant-schemas'
    ],
    python_requires='>=3.6',
    zip_safe=False,
)
