import os
from itertools import chain

from setuptools import setup, Command, find_packages


def packages_for(*names):
    return sorted(list(names) + list(chain.from_iterable(
        ['{}.{}'.format(name, p) for p in find_packages(name)]
        for name in names)))


setup(
    name='styxapi',
    version='3.0.0',
    packages=packages_for('styx'),
    install_requires=[
        "Flask>=1.0.4",
        "pyyaml>=5.4.1",
    ],
    extras_require={
        'dev': [
            'pycodestyle==2.7.0',
            'pytest==6.2.4',
            'pylint==2.9.6',
        ]
    },
    entry_points={}
)
