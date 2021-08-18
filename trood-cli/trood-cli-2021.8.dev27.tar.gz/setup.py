import os

from setuptools import setup, find_packages


def get_version():
    with open(os.path.join(os.path.curdir, 'VERSION')) as version_file:
        return version_file.read().strip()


setup(
    name='trood-cli',
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
    author='Trood Inc',
    url='',
    install_requires=[
        u'requests==2.22.0', 'click', 'pyfiglet', 'tabulate', 'keyring'
    ],
    entry_points='''
        [console_scripts]
        trood=trood.cli.trood:trood
    '''
)