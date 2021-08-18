# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kubernetes-stubs', 'kubernetes_ext']

package_data = \
{'': ['*'],
 'kubernetes-stubs': ['client/*',
                      'client/api/*',
                      'client/models/*',
                      'config/*']}

setup_kwargs = {
    'name': 'kubernetes-stubs',
    'version': '18.20.0',
    'description': 'Type stubs for the Kubernetes Python API client',
    'long_description': "# kubernetes-stubs\n\n[![PyPI](https://img.shields.io/pypi/v/kubernetes-stubs)](https://pypi.org/project/kubernetes-stubs/)\n\nPython type stubs for the [Kubernetes API client](https://github.com/kubernetes-client/python).\nThe version numbers of this package track upstream's. PRs to fix bugs are\nwelcomed.\n\n## Usage\n\n```\npip install kubernetes-stubs\n```\n",
    'author': 'Nikhil Benesch',
    'author_email': 'nikhil.benesch@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
