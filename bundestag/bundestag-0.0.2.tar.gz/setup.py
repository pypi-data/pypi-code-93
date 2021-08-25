# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bundestag']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'fastai>=2.5.2,<3.0.0',
 'fastcore>=1.3.26,<2.0.0',
 'fastparquet>=0.7.1,<0.8.0',
 'gensim>=4.0.1,<5.0.0',
 'ipywidgets>=7.6.3,<8.0.0',
 'loguru>=0.5.3,<0.6.0',
 'matplotlib>=3.4.3,<4.0.0',
 'openpyxl>=3.0.7,<4.0.0',
 'pandas>=1.3.2,<2.0.0',
 'plotly>=5.2.1,<6.0.0',
 'seaborn>=0.11.2,<0.12.0',
 'sklearn>=0.0,<0.1',
 'spacy>=3.1.2,<4.0.0',
 'xlrd>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'bundestag',
    'version': '0.0.2',
    'description': "Download, parse and analyse votes in the german federal parliament, aka 'Bundestag'",
    'long_description': None,
    'author': 'eschmidt42',
    'author_email': '11818904+eschmidt42@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
