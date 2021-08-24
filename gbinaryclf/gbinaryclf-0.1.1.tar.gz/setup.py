# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gbinaryclf']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'gbinaryclf',
    'version': '0.1.1',
    'description': 'Generic Python Package for Binary Classifications',
    'long_description': '# gbinaryclf\n\n<div align="right">\n\n[![Build status](https://github.com/altcp/gbinaryclf/workflows/build/badge.svg?branch=master&event=push)](https://github.com/altcp/gbinaryclf/actions?query=workflow%3Abuild)\n[![pypi](https://img.shields.io/pypi/v/gbinaryclf.svg)](https://pypi.python.org/pypi/gbinaryclf)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/altcp/gbinaryclf/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n</div>\n\nGeneric Python Package for Binary Classifications that seeks to include the latest over time and making it easy to use. &nbsp;\nThus, creating something that is current and stable for non-profit or social use.\n<p>&nbsp;</p>\n\n## Usage\n\nSee -> ./tests/test_example/test_hello.py\n<p>&nbsp;</p>\n\n\n## Features \n\n<div align="right">\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/altcp/gbinaryclf/blob/master/.pre-commit-config.yaml)\n\n</div>\n\n* Features\n\n<p>&nbsp;</p>\n\n\n\n## Why\n\n* https://www.clinfo.eu/mean-median/\n* https://www.health.harvard.edu/blog/the-11-most-expensive-medications-201202094228\n<p>&nbsp;</p>\n\n\n\n## Releases\n\n<div align="right">\n\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/altcp/gbinaryclf/releases)\n\n</div>\n\nYou can see the list of available releases on the [GitHub Releases](https://github.com/altcp/gdemandfcast/releases) page. &nbsp;\nWe use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes.\n<p>&nbsp;</p>\n\n\n\n## License\n\n<div align="right">\n\n[![License](https://img.shields.io/github/license/altcp/gbinaryclf)](https://github.com/altcp/gbinaryclf/blob/master/LICENSE)\n\n</div>\n\nThis project is licensed under the terms of the `GNU GPL v3.0` license.\n<p>&nbsp;</p>\n\n\n\n## 📃 Citation\n<p>&nbsp;</p>\n\n```bibtex\n@misc{gbinaryclf,\n  author = {altcp},\n  title = {Generic Python Package for Binary Classifications},\n  year = {2021},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {https://github.com/altcp/gbinaryclf}}\n}\n```\n<p>&nbsp;</p>\n\n\n\n## Credits \n<div align="right">\n\n[![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\n</div>\n\nThis project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n',
    'author': 'altcp',
    'author_email': 'colab.tcp@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/altcp/gbinaryclf',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
