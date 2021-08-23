#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0','vcrpy>=4.1.1','python-dotenv>=0.17.1','requests','numpy']

test_requirements = ['pytest>=3', ]

setup(
    author="Wilham Opoku Danquah",
    author_email='wilhamlynce27@gmail.com',
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
    description="Python Library for the Arkesel API ",
    entry_points={
        'console_scripts': [
            'arkesel_python=arkesel_python.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='arkesel_python',
    name='arkesel_python',
    packages=find_packages(include=['arkesel_python', 'arkesel_python.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/wilham-lynce/arkesel_python',
    download_url='https://github.com/wilham-lynce/arkesel_python/archive/refs/tags/0.1.0.tar.gz',
    version='0.1.0',
    zip_safe=False,
)
