# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_vendoring']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.1.8,<2.0.0']

entry_points = \
{'poetry.application.plugin': ['foo-command = '
                               'poetry_vendoring.plugin:VendorPlugin']}

setup_kwargs = {
    'name': 'poetry-vendoring',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'mohamedarzikiwm',
    'author_email': 'mohamed.a@wemaintain.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
