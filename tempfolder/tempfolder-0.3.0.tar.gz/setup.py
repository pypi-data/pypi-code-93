# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tempfolder']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tempfolder',
    'version': '0.3.0',
    'description': "🗂 Easily create temporary folders, add files into them and don't worry about deleting them, tempfolder will take care",
    'long_description': None,
    'author': 'Jorge Alvarado',
    'author_email': 'alvaradosegurajorge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
