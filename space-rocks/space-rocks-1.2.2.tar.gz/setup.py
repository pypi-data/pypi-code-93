# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rocks']

package_data = \
{'': ['*']}

install_requires = \
['aiodns>=3.0.0,<4.0.0',
 'aiohttp>=3.7.4,<4.0.0',
 'cchardet>=2.1.7,<3.0.0',
 'click>=8.0.1,<9.0.0',
 'iterfzf>=0.5.0,<0.6.0',
 'matplotlib>=3.4.3,<4.0.0',
 'nest-asyncio>=1.5.1,<2.0.0',
 'numpy>=1.21.2,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'requests>=2.26.0,<3.0.0',
 'rich>=10.7.0,<11.0.0',
 'tqdm>=4.62.1,<5.0.0']

extras_require = \
{'docs': ['sphinx>=3,<4',
          'sphinx-redactor-theme>=0.0.1,<0.0.2',
          'sphinx-click>=2.5.0,<3.0.0']}

entry_points = \
{'console_scripts': ['rocks = rocks.cli:cli_rocks']}

setup_kwargs = {
    'name': 'space-rocks',
    'version': '1.2.2',
    'description': 'Python client for SsODNet data access.',
    'long_description': '![python version](https://img.shields.io/pypi/pyversions/space-rocks)\n![PyPI](https://img.shields.io/pypi/v/space-rocks) [![Documentation Status](https://readthedocs.org/projects/rocks/badge/?version=latest)](https://rocks.readthedocs.io/en/latest/?badge=latest) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n# rocks\n\n*Disclaimer: The SsODNet service and its database are in an alpha version and under constant revision. The provided values and access methods may change without notice.*\n\n## Features\n\nCommand-line exploration and scripted retrieval of asteroid data.\n\n## Install\n\nInstall from PyPi using `pip`:\n\n     pip install space-rocks\n\n## Documentation\n\nCheck out the documentation at [rocks.readthedocs.io](https://rocks.readthedocs.io/en/latest/).\n',
    'author': 'Max Mahlke',
    'author_email': 'max.mahlke@oca.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rocks.readthedocs.io/en/latest/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
