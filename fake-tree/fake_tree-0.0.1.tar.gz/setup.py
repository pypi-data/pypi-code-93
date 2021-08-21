#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Hung Nguyen Thanh",
    author_email='hungnt89@gmail.com',
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
    description="Fake Tree creates a fake directory tree and files with no content to practice manipulating files.",
    entry_points={
        'console_scripts': [
            'fake_tree=fake_tree.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='fake_tree',
    name='fake_tree',
    packages=find_packages(include=['fake_tree', 'fake_tree.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/hungntgrb/fake_tree',
    version='0.0.1',
    zip_safe=False,
)
