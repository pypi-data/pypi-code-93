# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['owout']

package_data = \
{'': ['*']}

install_requires = \
['pyowo>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'owout',
    'version': '0.1.1',
    'description': 'Convert console output into owo.',
    'long_description': '# owout\n\nChange all console output to its owofied version.\n\n## Installation\n\n`pip install owout`\n\n## Usage\n\n```py\nimport owout\n\n# Thats it!\n```\n',
    'author': 'vcokltfre',
    'author_email': 'vcokltfre@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vcokltfre/owout',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
