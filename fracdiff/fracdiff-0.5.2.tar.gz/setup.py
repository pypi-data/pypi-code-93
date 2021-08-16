# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fracdiff', 'fracdiff.torch']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.18.0,<2.0.0',
 'scikit-learn>=0.24.0,<0.25.0',
 'scipy>=1.4.1,<2.0.0',
 'statsmodels>=0.12.0,<0.13.0']

extras_require = \
{'torch': ['torch>=1.9.0,<2.0.0']}

setup_kwargs = {
    'name': 'fracdiff',
    'version': '0.5.2',
    'description': 'Super-fast fractional differentiation.',
    'long_description': None,
    'author': 'Shota Imaki',
    'author_email': 'shota.imaki.0801@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fracdiff/fracdiff',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.13,<4.0.0',
}


setup(**setup_kwargs)
