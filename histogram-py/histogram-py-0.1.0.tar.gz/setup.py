# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['histogram']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.0,<2.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'histogram-py',
    'version': '0.1.0',
    'description': 'A pandas extension to open Dataframes & Series in histogram.dev',
    'long_description': '# Histogram\n\nA pandas extension to open Dataframes & Series in histogram.de\n\n\n## Usage/Examples\n\n```python\nimport histogram # Import at least once, anywhere\n\ndf.histogram.plot()\n\n```\n\n',
    'author': 'Tyler Cosgrove',
    'author_email': 'tyler@datawhys.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://histogram.dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
