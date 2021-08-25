#!/usr/bin/env python3
import pathlib

import setuptools
from neuralspace import VERSION


here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

core_requirements = [
    "requests~=2.25.1",
    "aiohttp~=3.7.4",
    "click~=8.0.1",
    "randomname~=0.1.3",
    "aiohttp~=3.7.4",
    "tqdm~=4.61.2",
    "coloredlogs~=15.0.1",
    "prettytable~=2.1.0",
    "rich~=10.7.0",
    "simple-term-menu~=1.3.0"
]

extras = {}

setuptools.setup(
    name='neuralspace',
    description="A Python CLI for NeuralSpace APIs",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://docs.neuralspace.ai',
    author='Ayushman Dash',
    author_email='ayushman@neuralspace.ai',
    version=VERSION,
    install_requires=core_requirements,
    extras_require=extras,
    python_requires='>=3.7,<3.9',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    include_package_data=True,
    package_data={
        "data": ["*.txt"]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={"console_scripts": ["neuralspace = neuralspace.cli:entrypoint"]},
)
