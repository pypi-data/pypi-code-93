# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oplusclient',
 'oplusclient.endpoints',
 'oplusclient.models',
 'oplusclient.tools']

package_data = \
{'': ['*'], 'oplusclient.tools': ['resources/*']}

install_requires = \
['pandas>=1.0.4,<2.0.0', 'requests>=2.23,<3.0']

setup_kwargs = {
    'name': 'oplusclient',
    'version': '1.8.1',
    'description': 'A python client for Oplus',
    'long_description': "# Oplusclient\n\n![GitHub](https://img.shields.io/github/license/openergy/oplusclient?color=brightgreen)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/oplusclient)\n![PyPI](https://img.shields.io/pypi/v/oplusclient)\n\nOplusclient is a Python package providing a client for working with Openergy's Oplus platform.\n\n## Documentation\n\nThe official documentation is hosted on readthedocs.io : https://oplusclient.readthedocs.io\n\n## License\n\n[Mozilla Public License Version 2.0](./LICENSE.txt)",
    'author': 'Openergy dev team',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/openergy/oplusclient',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
