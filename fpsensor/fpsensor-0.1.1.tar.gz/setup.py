# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fpsensor']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=8.3.0,<9.0.0', 'embutils>=0.2.2,<0.3.0']

entry_points = \
{'console_scripts': ['cover = scripts.poetry:run_coverage',
                     'docs = scripts.poetry:run_docs',
                     'html = scripts.poetry:run_html',
                     'linter = scripts.poetry:run_linter',
                     'test = scripts.poetry:run_test',
                     'version = scripts.poetry:run_version']}

setup_kwargs = {
    'name': 'fpsensor',
    'version': '0.1.1',
    'description': 'Python library for ZhianTec fingerprint sensors',
    'long_description': '# FPSensor \n[![PyPI version](https://badge.fury.io/py/fpsensor.svg)](https://badge.fury.io/py/fpsensor) \n[![Docs Status](https://readthedocs.org/projects/fpsensor/badge/?version=latest)](https://fpsensor.readthedocs.io/en/latest/?badge=latest)\n[![License](https://img.shields.io/:license-mit-blue.svg?style=flat-square)](https://badges.mit-license.org)\n\nThis library allows to use the ZhianTec ZFM-x fingerprint sensors. Some other models like R302, R303, R305, R306, R307, \nR551 and FPM10A also work.\n\n**Note:** This library is based on [pyfingerprint](https://github.com/bastianraschke/pyfingerprint) and \n[embutils](https://github.com/cwichel/embutils). \n\n## Installation\nYou can get the packaged version from [PyPI](https://pypi.org/project/fpsensor/):\n```\npip install fpsensor\n```\n',
    'author': 'Christian Wiche',
    'author_email': 'cwichel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cwichel/fpsensor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
