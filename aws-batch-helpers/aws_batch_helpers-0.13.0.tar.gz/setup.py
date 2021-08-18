#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
import versioneer

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['boto3', 'boto3-stubs[s3,ec2,batch,logs]']

test_requirements = ['pytest>=3', ]

setup(
    author="Jillian Rowe",
    author_email='jillian.e.rowe@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Helpers for running jobs on AWS Batch",
    entry_points={
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='aws_batch_helpers',
    name='aws_batch_helpers',
    packages=find_packages(include=['aws_batch_helpers', 'aws_batch_helpers.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/jerowe/aws_batch_helpers',
    # version='0.1.0',
    zip_safe=False,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
