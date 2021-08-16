# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_pep440_plugin']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.2.0a2,<2.0.0']

entry_points = \
{'poetry.application.plugin': ['poetry-workspace-plugin = '
                               'poetry_workspace.plugin:WorkspacePlugin']}

setup_kwargs = {
    'name': 'poetry-pep440-plugin',
    'version': '0.1.0',
    'description': 'Loosens validation for PEP440 version constraints',
    'long_description': '',
    'author': 'Martin Liu',
    'author_email': 'martin.xs.liu@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
