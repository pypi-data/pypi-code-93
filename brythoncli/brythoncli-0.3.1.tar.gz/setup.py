"""Another command line interface for Brython."""
import re

from os.path import join, dirname
from setuptools import setup, find_packages


# reading package version (same way the sqlalchemy does)
with open(join(dirname(__file__), 'brythoncli', '__init__.py')) as v_file:
    package_version = re.compile('.*__version__ = \'(.*?)\'', re.S).\
        match(v_file.read()).group(1)


dependencies = [
    'easycli',
    'brython',
]


setup(
    name='brythoncli',
    description='Another command line interface for the Brython.',
    version=package_version,
    packages=find_packages(),
    install_requires=dependencies,
    include_package_data=True,
    license='MIT',
    url='http://github.com/pylover/brythoncli',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    entry_points={
        'console_scripts': [
            'brython = brythoncli:Brython.quickstart',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Text Processing',
    ]
)
