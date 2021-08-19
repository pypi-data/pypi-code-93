# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pfzy']

package_data = \
{'': ['*']}

extras_require = \
{'docs': ['Sphinx>=4.1.2,<5.0.0',
          'furo>=2021.8.17-beta.43,<2022.0.0',
          'myst-parser>=0.15.1,<0.16.0',
          'sphinx-autobuild>=2021.3.14,<2022.0.0',
          'sphinx-copybutton>=0.4.0,<0.5.0']}

setup_kwargs = {
    'name': 'pfzy',
    'version': '0.1.0',
    'description': 'Python port of the fzy fuzzy string matching algorithm',
    'long_description': None,
    'author': 'Kevin Zhuang',
    'author_email': 'kevin7441@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
