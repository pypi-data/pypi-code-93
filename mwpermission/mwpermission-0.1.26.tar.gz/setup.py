from setuptools import setup, find_packages
from codecs import open
from os import path
import os

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f),encoding='utf8').read().strip()

setup(
    name='mwpermission',
    version='0.1.26',
    description='maxwin permission ',
    # long_description= '\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
    url='https://bitbucket.org/maxwin-inc/mwpermission/src',  # Optional
    author='cxhjet',  # Optional
    author_email='cxhjet@qq.com',  # Optional
    packages=['mwpermission'],
    package_data={
        '': ['*.*']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'flask>=0.11.1'
    ]
)
