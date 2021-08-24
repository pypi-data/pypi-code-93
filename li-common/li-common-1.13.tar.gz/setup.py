# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='li-common',
    version='1.13',
    url='https://github.com/lojaintegrada/LI-Common',
    license='MIT',
    description='Lib para funcionalidades comuns aos aplicativos da Loja Integrada',
    author=u'Loja Integrada',
    author_email='suporte@lojaintegrada.com.br',
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'flask_restful==0.3.4',
        'celery==3.1.18',
        'requests==2.7.0',
        'boto==2.42.0',
        'pyelasticsearch==1.4',
        'redis==2.10.3',
        'pycrypto==2.6.1',
        'jsonpickle',
        'blinker==1.4', # Raven precisa para funcionar
        'raven==5.5.0', # Envia dados para Sentry
        'selenium==3.0.1',
    ],
)
