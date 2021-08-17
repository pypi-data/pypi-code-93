# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyexeqjy']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pyexeqjy = pyexeqjy:entry.main']}

setup_kwargs = {
    'name': 'pyexeqjy',
    'version': '0.1.0',
    'description': 'This is a cli for developer of remote vehicle side',
    'long_description': None,
    'author': 'qiujingyu',
    'author_email': 'qiujingyu@momenta.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
