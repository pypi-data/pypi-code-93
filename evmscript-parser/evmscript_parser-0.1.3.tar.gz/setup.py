"""Installation of EVMScripts parser package."""
from setuptools import setup, find_packages

from evmscript_parser.package import NAME, CLI_NAME

setup(
    name=NAME,
    description='Parser for human-readable decoding of EVM scripts.',
    author='Dmitri Ivakhnenko',
    author_email='dmit.ivh@gmail.com',
    use_scm_version={
        'root': '.',
        'relative_to': __file__,
        'local_scheme': 'node-and-timestamp'
    },
    setup_requires=['setuptools_scm'],
    packages=find_packages(
        where='.',
        exclude='tests'
    ),
    entry_points={
        'console_scripts': [
            f'{CLI_NAME}=evmscript_parser.__main__:main'
        ]
    },
    install_requires=[
        'requests~=2.26.0',
        'pysha3~=1.0.0'
    ]
)
