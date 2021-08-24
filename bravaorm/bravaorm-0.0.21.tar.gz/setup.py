#!/usr/bin/env python

import setuptools

readme = open('README.md').read()

with open('requirements.txt') as reqs:
    requirements = reqs.read().split()

setuptools.setup(
    name='bravaorm',
    version='0.0.21',
    description='Python ORM for MySQL',
    author='Roberto Neves',
    author_email='robertonsilva@gmail.com',
    url='https://github.com/robertons/bravaorm',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Natural Language :: Portuguese (Brazilian)',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='orm, datamodel, database, model, entity, sdk, mysql, mariadb'
)
