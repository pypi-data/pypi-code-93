# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sovol_xy', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['bumpversion[dev]>=0.6.0,<0.7.0',
 'fire==0.4.0',
 'livereload[test]>=2.6.3,<3.0.0',
 'pyserial>=3.5,<4.0']

extras_require = \
{'dev': ['tox>=3.20.1,<4.0.0',
         'virtualenv>=20.2.2,<21.0.0',
         'pip>=20.3.1,<21.0.0',
         'twine>=3.3.0,<4.0.0',
         'pre-commit>=2.12.0,<3.0.0',
         'toml>=0.10.2,<0.11.0'],
 'doc': ['mkdocs>=1.1.2,<2.0.0',
         'mkdocs-include-markdown-plugin>=1.0.0,<2.0.0',
         'mkdocs-material>=6.1.7,<7.0.0',
         'mkdocstrings>=0.13.6,<0.14.0',
         'mkdocs-autorefs==0.1.1'],
 'test': ['black==20.8b1',
          'isort==5.6.4',
          'flake8==3.8.4',
          'flake8-docstrings>=1.6.0,<2.0.0',
          'pytest==6.1.2',
          'pytest-cov==2.10.1']}

entry_points = \
{'console_scripts': ['sovol_xy = sovol_xy.cli:main']}

setup_kwargs = {
    'name': 'sovol-xy',
    'version': '0.1.1',
    'description': 'Library for controlling the Sovol-SO1 xy plotter using the Marlin Firmware.',
    'long_description': '# Sovol XY Plotter\n\n\n<p align="center">\n<a href="https://pypi.python.org/pypi/sovol_xy">\n    <img src="https://img.shields.io/pypi/v/sovol_xy.svg"\n        alt = "Release Status">\n</a>\n\n<a href="https://github.com/cwoodall/sovol_xy/actions">\n    <img src="https://github.com/cwoodall/sovol_xy/actions/workflows/main.yml/badge.svg?branch=release" alt="CI Status">\n</a>\n\n<a href="https://sovol-xy.readthedocs.io/en/latest/?badge=latest">\n    <img src="https://readthedocs.org/projects/sovol-xy/badge/?version=latest" alt="Documentation Status">\n</a>\n\n<a href="https://pyup.io/repos/github/cwoodall/sovol_xy/">\n<img src="https://pyup.io/repos/github/cwoodall/sovol_xy/shield.svg" alt="Updates">\n</a>\n\n</p>\n\n\nLibrary for controlling the Sovol-SO1 xy plotter using the Marlin Firmware\n\n\n* Free software: MIT\n* Documentation: <https://sovol-xy.readthedocs.io>\n\n\n## Features\n\n* TODO\n\n## Credits\n\nThis package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [zillionare/cookiecutter-pypackage](https://github.com/zillionare/cookiecutter-pypackage) project template.\n',
    'author': 'Christopher Woodall',
    'author_email': 'chris@cwoodall.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cwoodall/sovol_xy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
