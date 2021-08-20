# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hbase', 'hbase.models']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2', 'uplink>=0.9.4']

setup_kwargs = {
    'name': 'hbase',
    'version': '0.1.3',
    'description': 'Hbase REST API client built using uplink',
    'long_description': '<h1 align="center">\n   <strong>hbase</strong>\n</h1>\n\n<p align="center">\n    <a href="https://codecov.io/gh/ghandic/hbase" target="_blank">\n        <img src="https://img.shields.io/codecov/c/github/ghandic/hbase?color=%2334D058" alt="Coverage">\n    </a>\n    <a href="https://ghandic.github.io/hbase" target="_blank">\n        <img src="https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat" alt="Docs">\n    </a>\n    <a href="https://pypi.org/project/hbase/" target="_blank">\n        <img src="https://img.shields.io/pypi/v/hbase.svg" alt="PyPI Latest Release">\n    </a>\n    <br /><a href="https://github.com/ghandic/hbase/blob/main/LICENSE" target="_blank">\n        <img src="https://img.shields.io/github/license/ghandic/hbase.svg" alt="License">\n    </a>\n    <a href="https://github.com/psf/black" target="_blank">\n        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">\n    </a>\n</p>\n\nHbase REST API client built using uplink\n\n## Main Features\n\n- ... # TODO: Add features\n\n## Installation\n\n<div class="termy">\n\n```console\n$ pip install hbase\n\n---> 100%\n```\n\n</div>\n\n## Usage\n\n### Basic 😊\n\n```python\nimport hbase\n\n...\n```\n\nResults in ... # TODO: Add example\n\n```python\n# TODO: Add example\n```\n\n## Credits\n\n- # TODO: Add credits\n\n## License\n\n* [MIT License](/LICENSE)\n',
    'author': 'Andy Challis',
    'author_email': 'andrewchallis@hotmail.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CapgeminiInventIDE/hbase',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
