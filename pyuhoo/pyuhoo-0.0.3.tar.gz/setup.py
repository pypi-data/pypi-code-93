# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyuhoo']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0', 'click>=8.0.1,<9.0.0', 'pycryptodome>=3.10.1,<4.0.0']

entry_points = \
{'console_scripts': ['pyuhoo-cli = pyuhoo.cli:cli']}

setup_kwargs = {
    'name': 'pyuhoo',
    'version': '0.0.3',
    'description': 'Python API for talking to uHoo consumer API',
    'long_description': '# pyuhoo\n\n[![PyPi version](https://img.shields.io/pypi/v/pyuhoo.svg)](https://pypi.python.org/pypi/pyuhoo/)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/csacca/pyuhoo/master.svg)](https://results.pre-commit.ci/latest/github/csacca/pyuhoo/master)\n![ci workflow](https://github.com/csacca/pyuhoo/actions/workflows/ci.yaml/badge.svg)\n\nPython API for talking to uHoo consumer API\n\nPlease note that this is a non-public API that has been reverse-engineered from mobile\napps. It is likely to break unexpectedly when uHoo changes the API.\n',
    'author': 'Christopher Sacca',
    'author_email': 'csacca@csacca.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/csacca/pyuhoo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
