# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['great_text']

package_data = \
{'': ['*']}

install_requires = \
['pyfiglet>=0.8.post1,<0.9', 'termcolor>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'great-text',
    'version': '0.1.1',
    'description': 'Add font and color to your Python text.',
    'long_description': '# great-text',
    'author': 'Deepak',
    'author_email': 'info.deepakpatidar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeepakDarkiee/great-text.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
