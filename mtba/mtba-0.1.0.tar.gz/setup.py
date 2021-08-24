# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mtba']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'mtba',
    'version': '0.1.0',
    'description': 'meituan ba auth',
    'long_description': None,
    'author': 'huoyinghui',
    'author_email': 'hyhlinux@163.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pydtools/mtba/',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
