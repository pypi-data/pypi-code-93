# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pbf_file_size_estimation']

package_data = \
{'': ['*']}

install_requires = \
['djangorestframework>=3.12.4,<4.0.0']

setup_kwargs = {
    'name': 'geometalab.osm-pbf-file-size-estimation-service',
    'version': '3.0.0',
    'description': 'Rough pbf estimate of a certain extent.',
    'long_description': None,
    'author': 'Geometa Lab',
    'author_email': 'geometalab@hsr.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/geometalab/osm-pbf-file-size-estimation-service',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
