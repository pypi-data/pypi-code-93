# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cohmetrix_br']

package_data = \
{'': ['*']}

install_requires = \
['Pyphen>=0.10.0,<0.11.0',
 'Unidecode>=1.2.0,<2.0.0',
 'billiard>=3.6.4,<4.0.0',
 'fastapi>=0.65.2,<0.66.0',
 'gensim>=4.0.1,<5.0.0',
 'lexical-diversity>=0.1.1,<0.2.0',
 'nltk>=3.6.2,<4.0.0',
 'numpy>=1.20.3,<2.0.0',
 'orjson>=3.5.3,<4.0.0',
 'pandas>=1.2.4,<2.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'sklearn>=0.0,<0.1',
 'spacy>=3.0.6,<4.0.0',
 'textblob>=0.15.3,<0.16.0',
 'uvicorn>=0.14.0,<0.15.0']

setup_kwargs = {
    'name': 'cohmetrix-br',
    'version': '0.1.0',
    'description': 'A Brazilian-Portuguese version of cohmetrix',
    'long_description': None,
    'author': 'Rafael Melo',
    'author_email': 'rafaelflmello@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
