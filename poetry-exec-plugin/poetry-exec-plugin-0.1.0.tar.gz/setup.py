# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_exec_plugin']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.2.0.a2,<2.0.0',
 'simple-chalk>=0.1.0,<0.2.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'poetry.application.plugin': ['exec = poetry_exec_plugin.plugin:ExecPlugin']}

setup_kwargs = {
    'name': 'poetry-exec-plugin',
    'version': '0.1.0',
    'description': 'A plugin for poetry that allows you to execute scripts defined in your pyproject.toml, just like you can in npm or pipenv.',
    'long_description': 'None',
    'author': 'keattang',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
