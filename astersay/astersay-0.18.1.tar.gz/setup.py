#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
from setuptools import setup

# Dynamically calculate the version based on astersay.VERSION.
version = __import__('astersay').get_version()

with open('README.rst', 'r') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = [
        l.split('#', 1)[0].strip() for l in f.read().splitlines()
        if not l.strip().startswith('#')
    ]

with open('requirements-optional.txt') as f:
    dev_requirements = [
        l.split('#', 1)[0].strip() for l in f.read().splitlines()
        if not l.strip().startswith('#')
    ]

setup(
    name='astersay',
    version=version,
    description=(
        'This is a Python library for Asterisk to work with Yandex voice models.'
    ),
    long_description=long_description,
    author='Grigoriy Kramarenko',
    author_email='root@rosix.ru',
    url='https://gitlab.com/djbaldey/asterisk-dialogs/',
    license='BSD License',
    platforms='any',
    zip_safe=False,
    packages=['astersay'],
    scripts=[
        'scripts/astersay',
        'scripts/astersay-cgi',
        'scripts/astersay-dev',
        'scripts/astersay-t2v',
    ],
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'dev': dev_requirements,
    },
    classifiers=[
        # List of Classifiers: https://pypi.org/classifiers/
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: Russian',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications :: Internet Phone',
        'Topic :: Communications :: Telephony',
    ],
)
