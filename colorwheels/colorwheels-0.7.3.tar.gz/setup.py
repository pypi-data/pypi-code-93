"""colorwheels setuptools setup module
"""

# description of options of setup.py in https://github.com/pypa/sampleproject

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# read config.py settings, including version
exec(open(here / 'src/colorwheels/config.py').read())

setup(
    name='colorwheels',
    version=__version__,
    description='colorwheels - an endless color generator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/quantumspaces/colorwheels',
    author='Quantum Spaces',
    author_email='quantumspaces@outlook.com',

    classifiers=[ # List of valid classifiers: https://pypi.org/classifiers/
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords='development, color',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7, <4',

    install_requires = [
        'dataclasses-json',
        'PyYAML'
    ],

    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },

    project_urls={
        'Bug Reports': 'https://github.com/quantumspaces/colorwheels/issues',
        'Source': 'https://github.com/quantumspaces/colorwheels',
    },
)
