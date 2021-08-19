#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from setuptools import setup
from setuptools import setup#, find_namespace_packages
def readme():
    with open('README.rst', encoding='utf-8') as f:
        return f.read()

setup(
     name='starfishX',   # This is the name of your PyPI-package.
     version='0.155531',  # Update the version number for new releases
     author='nattapat attiratanasunthron',
     author_email='tapattan@gmail.com',
     url='https://github.com/tapattan/starfishX',
     #packages=['starfishX'],
     packages=['starfishX','starfishX.peterlynch','starfishX.volatility'],
     #package_data={'starfishX': ['sa_model.h5','dictionary.json']},
     #packages=find_namespace_packages(include=['starfishX','starfishX.peterlynch']),
     zip_safe = False,
     keywords=['starfishx','finance','การลงทุน','หุ้น','peterlynch'],
     description='Get data of stock exchange thailand (SET)',
     long_description=readme(),
     long_description_content_type='text/markdown',
     install_requires=['requests','beautifulsoup4','urllib3','pyqt5','pandas','html5lib','ffn','tqdm','seaborn','scipy','sklearn','squarify','selenium','pythainlp'], #
)
