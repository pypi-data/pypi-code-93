#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'numpy']

test_requirements = ['pytest>=3', ]

setup(
    author="Joy He",
    author_email='jh4337@columbia.edu',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="SQL Translate stores database info and generates complex sql queries so people who don't know sql can access the data they need in a user friendly way",
    entry_points={
        'console_scripts': [
            'sqltranslate=sqltranslate.__main__:main',
        ],
    },
    install_requires=requirements,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords='sqltranslate',
    name='sqltranslate',
    packages=find_packages(include=['sqltranslate', 'sqltranslate.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/joyhe208/pkg_sqltranslate',
    version='0.1.4',
    zip_safe=False,
    license='MIT',
    download_url='https://github.com/joyhe208/pkg_sqltranslate/archive/refs/tags/0.1.4.tar.gz'
)
