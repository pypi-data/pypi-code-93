# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['understory_cloud',
 'understory_cloud.templates',
 'understory_cloud.understory_stream',
 'understory_cloud.understory_stream.templates']

package_data = \
{'': ['*'], 'understory_cloud': ['static/*']}

install_requires = \
['understory']

entry_points = \
{'web.apps': ['understory_cloud = understory_cloud:app',
              'understory_stream = understory_cloud.understory_stream:app']}

setup_kwargs = {
    'name': 'understory.cloud',
    'version': '0.0.4',
    'description': 'Navigate the various projects tangential to the understory.',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'angelo@lahacker.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://understory.cloud/understory.cloud.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
