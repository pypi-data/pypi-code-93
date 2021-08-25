# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['textual', 'textual.layouts', 'textual.views', 'textual.widgets']

package_data = \
{'': ['*']}

install_requires = \
['rich>=10.7.0,<11.0.0']

extras_require = \
{':python_version < "3.8"': ['typing-extensions>=3.10.0,<4.0.0']}

setup_kwargs = {
    'name': 'textual',
    'version': '0.1.10',
    'description': 'Text User Interface using Rich',
    'long_description': None,
    'author': 'Will McGugan',
    'author_email': 'willmcgugan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/willmcgugan/textual',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
