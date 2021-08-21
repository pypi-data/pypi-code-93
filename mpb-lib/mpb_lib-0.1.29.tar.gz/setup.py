from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mpb_lib',
    packages=find_packages(),

    version='0.1.29', # バージョン

    license='MIT', # ライセンス

    install_requires=[],

    author='Atsushi Shibata',
    author_email='shibata@m-info.co.jp',

    url='',

    description='A library for minpro.',
    long_description='',
    long_description_content_type='text/markdown',
    keywords='',

    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)