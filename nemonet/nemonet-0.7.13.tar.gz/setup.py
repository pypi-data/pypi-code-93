# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nemonet',
 'nemonet.cvision',
 'nemonet.engines',
 'nemonet.runner',
 'nemonet.screencast',
 'nemonet.seleniumwebdriver',
 'nemonet.tests',
 'nemonet.tests.units']

package_data = \
{'': ['*']}

install_requires = \
['MouseInfo>=0.1.3,<0.2.0',
 'Pillow>=8.2.0,<9.0.0',
 'PyAutoGUI>=0.9.50,<0.10.0',
 'PyGetWindow>=0.0.8,<0.0.9',
 'PyMsgBox>=1.0.8,<2.0.0',
 'PyRect>=0.1.4,<0.2.0',
 'PyScreeze>=0.1.26,<0.2.0',
 'PyTweening>=1.0.3,<2.0.0',
 'PyWavelets>=1.1.1,<2.0.0',
 'atomicwrites>=1.4.0,<2.0.0',
 'attrs>=20.2.0,<21.0.0',
 'beautifulsoup4>=4.9.1,<5.0.0',
 'certifi>=2020.6.20,<2021.0.0',
 'colorama>=0.4.3,<0.5.0',
 'cycler>=0.10.0,<0.11.0',
 'decorator>=4.4.2,<5.0.0',
 'graphviz>=0.16.0,<0.17.0',
 'h5py>=3.1.0,<4.0.0',
 'imagehash>=4.2.0,<5.0.0',
 'imageio>=2.9.0,<3.0.0',
 'importlib-metadata>=1.7.0,<2.0.0',
 'imutils>=0.5.3,<0.6.0',
 'iniconfig>=1.0.1,<2.0.0',
 'kiwisolver>=1.2.0,<2.0.0',
 'lxml>=4.5.2,<5.0.0',
 'matplotlib>=3.3.2,<4.0.0',
 'more-itertools>=8.5.0,<9.0.0',
 'networkx>=2.5,<3.0',
 'numpy>=1.19.2,<2.0.0',
 'opencv-contrib-python>=4.4.0.42,<5.0.0.0',
 'packaging>=20.4,<21.0',
 'pluggy>=0.13.1,<0.14.0',
 'py>=1.9.0,<2.0.0',
 'pyparsing>=2.4.7,<3.0.0',
 'pyperclip>=1.8.0,<2.0.0',
 'pytest>=6.0.2,<7.0.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'requests>=2.25.1,<3.0.0',
 'scikit-image>=0.18.2,<0.19.0',
 'scipy>=1.5.2,<2.0.0',
 'selenium>=3.141.0,<4.0.0',
 'six>=1.15.0,<2.0.0',
 'soupsieve>=2.0.1,<3.0.0',
 'tifffile>=2020.9.3,<2021.0.0',
 'toml>=0.10.1,<0.11.0',
 'typer>=0.3.2,<0.4.0',
 'urllib3>=1.25.10,<2.0.0',
 'zipp>=3.1.0,<4.0.0']

entry_points = \
{'console_scripts': ['vision = nemonet.main:app']}

setup_kwargs = {
    'name': 'nemonet',
    'version': '0.7.13',
    'description': 'Visual testing framework. Combining selenium and computer vision.',
    'long_description': None,
    'author': 'Jan Rummens',
    'author_email': 'jan.rummens@nemo.be',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
