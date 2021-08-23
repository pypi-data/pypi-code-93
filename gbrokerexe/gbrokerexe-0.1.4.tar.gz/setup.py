# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gbrokerexe']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0', 'pandas>=1.3.2,<2.0.0', 'pytest>=6.2.4,<7.0.0']

setup_kwargs = {
    'name': 'gbrokerexe',
    'version': '0.1.4',
    'description': 'Generic Python Package for Brokerage and Trade Executions.',
    'long_description': '# gbrokerexe\n\n<div align="right">\n\n[![Build status](https://github.com/altcp/gbrokerexe/workflows/build/badge.svg?branch=master&event=push)](https://github.com/altcp/gbrokerexe/actions?query=workflow%3Abuild)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/altcp/gbrokerexe/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n[![pypi](https://img.shields.io/pypi/v/gbrokerexe.svg)](https://pypi.python.org/pypi/gbrokerexe)\n\n</div>\n\nGeneric Python Package for Brokerage and Trade Executions.\n<p>&nbsp;</p>\n\n\n\n## Features \n\n<div align="right">\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) \n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/altcp/gbrokerexe/blob/master/.pre-commit-config.yaml)\n\n</div>\n\n* oanda API \n* alpaca-trade API\n* others\n<p>&nbsp;</p>\n\n\n\n## Releases\n\n<div align="right">\n\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/altcp/gdemandfcast/releases)\n\n</div>\n\nYou can see the list of available releases on the [GitHub Releases](https://github.com/altcp/gdemandfcast/releases) page. &nbsp;\nWe use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes.\n<p>&nbsp;</p>\n\n\n\n## License\n\n<div align="right">\n\n[![License](https://img.shields.io/github/license/altcp/gbrokerexe)](https://github.com/altcp/gbrokerexe/blob/master/LICENSE)\n\n</div>\n\nThis project is licensed under the terms of the `GNU GPL v3.0` license.\n<p>&nbsp;</p>\n\n\n\n## 📃 Citation\n<p>&nbsp;</p>\n\n```bibtex\n@misc{gbrokerexe,\n  author = {altcp},\n  title = {Generic Python Package for Brokerage and Trade Executions},\n  year = {2021},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/altcp/gbrokerexe}}\n}\n```\n<p>&nbsp;</p>\n\n\n## Credits \n<div align="right">\n\n[![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\n</div>\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n',
    'author': 'altcp',
    'author_email': 'colab.tcp@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/altcp/gbrokerexe',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
