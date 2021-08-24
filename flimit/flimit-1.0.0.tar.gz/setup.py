# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flimit']

package_data = \
{'': ['*']}

install_requires = \
['psutil>=5.8.0,<6.0.0']

setup_kwargs = {
    'name': 'flimit',
    'version': '1.0.0',
    'description': 'Limit time and memory usage from a function',
    'long_description': '# Limit time and memory usage of a Python function\n\n## Installation\n\n```\npip install flimit\n```\n\n## Usage\n\n```python\nfrom flimit.memory import limit_memory\nfrom flimit.time import limit_time\n\n@limit_memory(10**9)\n@limit_time(60)\ndef f(...):  # f will have a limit of 1 Go allocation memory and 60 seconds computation time\n    ...\n```\n\n## Tests\n\n```\npython -m pytest tests\n```',
    'author': 'Quentin Fortier',
    'author_email': 'qpfortier@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fortierq/flimit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
