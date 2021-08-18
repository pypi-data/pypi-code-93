# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycln', 'pycln.utils']

package_data = \
{'': ['*']}

install_requires = \
['libcst>=0.3.10,<0.4.0',
 'pathspec>=0.8.0,<0.9.0',
 'pyyaml>=5.3.1,<6.0.0',
 'toml>=0.10.1,<0.11.0',
 'typer>=0.3.1,<0.4.0']

extras_require = \
{':python_version == "3.6"': ['dataclasses>=0.7,<0.8']}

entry_points = \
{'console_scripts': ['pycln = pycln.cli:app']}

setup_kwargs = {
    'name': 'pycln',
    'version': '1.0.3',
    'description': 'A formatter for finding and removing unused import statements.',
    'long_description': '<img src="https://raw.githubusercontent.com/hadialqattan/pycln/master/docs/_media/logo-background.png" width="100%" alt="Logo">\n\n<p align="center">\n    A formatter for finding and removing unused import statements.\n</p>\n\n<p align="center">\n    <a href="https://hadialqattan.github.io/pycln"><img src="https://img.shields.io/badge/For%20More%20Information%20See-Pycln%20Docs-B5FFB3.svg?style=flat-square" alt="Code style: prettier"></a>\n    <a href="https://github.com/hadialqattan/pycln/actions?query=workflow%3ACI"><img src="https://img.shields.io/github/workflow/status/hadialqattan/pycln/CI/master?label=CI&logo=github&style=flat-square" alt="CI"></a>\n    <a href="https://github.com/hadialqattan/pycln/actions?query=workflow%3ACD"><img src="https://img.shields.io/github/workflow/status/hadialqattan/pycln/CD?label=CD&logo=github&style=flat-square" alt="CD"></a>\n    <a href="https://www.codacy.com/manual/hadialqattan/pycln/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hadialqattan/pycln&amp;utm_campaign=Badge_Grade"><img src="https://img.shields.io/codacy/grade/e7c6c290c3c149e484634ac1905800d6/master?style=flat-square" alt="Codacy Badge"></a>\n    <a href="https://codecov.io/gh/hadialqattan/pycln"><img src="https://img.shields.io/codecov/c/gh/hadialqattan/pycln/master?token=VVYBDCZPHR&style=flat-square" alt="Codecov"></a>\n    <a href="https://codeclimate.com/github/hadialqattan/pycln/maintainability"><img src="https://img.shields.io/codeclimate/maintainability/hadialqattan/pycln?style=flat-square" alt="Maintainability"></a>\n</p>\n\n<p align="center">\n    <img src="https://img.shields.io/pypi/pyversions/pycln?style=flat-square" alt="PYPI - Python Version">\n    <a href="https://pypi.org/project/pycln/"><img src="https://img.shields.io/pypi/v/pycln?style=flat-square" alt="PYPI - Pycln Version"></a>\n    <a href="https://pypi.org/project/pycln/"><img src="https://img.shields.io/pypi/dm/pycln?color=dark-green&style=flat-square" alt="Downloads"></a>\n    <a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fhadialqattan%2Fpycln&count_bg=%2344CC10&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=true"/></a>\n    <a href="_blank"><img src="https://img.shields.io/tokei/lines/github.com/hadialqattan/pycln?style=flat-square" alt="Lines Of Code"></a>\n</p>\n\n<p align="center">\n    <a href="https://github.com/hadialqattan/pycln/fork"><img src="https://img.shields.io/github/forks/hadialqattan/pycln?style=flat-square" alt="Forks"></a>\n    <a href="https://github.com/hadialqattan/pycln/stargazers"><img src="https://img.shields.io/github/stars/hadialqattan/pycln?style=flat-square" alt="Stars"></a>\n    <a href="https://github.com/hadialqattan/pycln/issues"><img src="https://img.shields.io/github/issues/hadialqattan/pycln?style=flat-square" alt="Issues"></a>\n    <a href="https://github.com/hadialqattan/pycln/pulls"><img src="https://img.shields.io/github/issues-pr/hadialqattan/pycln?style=flat-square" alt="Pull Requests"></a>\n    <a href="https://github.com/hadialqattan/pycln/graphs/contributors"><img src="https://img.shields.io/github/contributors/hadialqattan/pycln?style=flat-square" alt="Contributors"></a>\n    <a href="https://github.com/hadialqattan/pycln/commits/master"><img src="https://img.shields.io/github/last-commit/hadialqattan/pycln.svg?style=flat-square" alt="Last Commit"></a>\n    <a href="https://github.com/hadialqattan/pycln/blob/master/LICENSE"><img src="https://img.shields.io/github/license/hadialqattan/pycln.svg?color=A31F34&style=flat-square" alt="License"></a>\n</p>\n\n<p align="center">\n    <a href="https://docutils.sourceforge.io/rst.html"><img src="https://img.shields.io/badge/docstrings-reStructuredText-gree.svg?style=flat-square" alt="Docstrings: reStructuredText"></a>\n    <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="Code style: black"></a>\n    <a href="https://github.com/prettier/prettier"><img src="https://img.shields.io/badge/code%20style-prettier-ff69b4.svg?style=flat-square" alt="Code style: prettier"></a>\n</p>\n\n---\n\n<p align="center">\nFor more information see: https://hadialqattan.github.io/pycln\n</p>\n',
    'author': 'Hadi Alqattan',
    'author_email': 'alqattanhadizaki@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://hadialqattan.github.io/pycln',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<3.10',
}


setup(**setup_kwargs)
