# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nepseutils']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=3.4.7,<4.0.0',
 'requests>=2.25.1,<3.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'tenacity>=7.0.0,<8.0.0']

setup_kwargs = {
    'name': 'nepseutils',
    'version': '0.2.2',
    'description': 'Collection of scripts to interact with NEPSE related websites!',
    'long_description': '# NEPSE Utils\nCollection of scripts to interact with NEPSE related sites.\n## Installation\n`pip install nepseutils`\n## Usage\n`python -m nepseutils`\nNote: New data file is created on the first launch!\n\n## Commands:\n|  Command      |  Description                 |\n|---------------|------------------------------|\n|`add`          | Add an account               |\n|`remove`       | Remove an account            |\n|`change lock`  | Change unlock password       |\n|`list accounts`| Show list of accounts        |\n|`list results` | Show list of results         |\n|`apply`        | Apply open issues            |\n|`status`       | Check IPO application status |\n|`result`       | Check IPO result             |\n|`exit`         | Exit the shell               |\n\n',
    'author': 'Daze',
    'author_email': 'dazehere@yandex.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/arpandaze/nepseutils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
