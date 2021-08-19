# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hydrosdk', 'hydrosdk.data']

package_data = \
{'': ['*']}

install_requires = \
['docker-image-py>=0.1.10,<0.2.0',
 'hydro-serving-grpc==3.0.0',
 'importlib_metadata>=1.7.0,<2.0.0',
 'numpy==1.18.3',
 'pandas>=1.1.5',
 'pydantic>=1.8.2,<2.0.0',
 'pyyaml>=5.4.1,<6.0.0',
 'requests==2.23.0',
 'requests_toolbelt>=0.9.1,<0.10.0',
 'sseclient-py>=1.7,<2.0',
 'tox>=3.23.1,<4.0.0']

extras_require = \
{':python_version < "3.7"': ['dataclasses==0.7']}

setup_kwargs = {
    'name': 'hydrosdk',
    'version': '3.0.0',
    'description': " This package's purpose is to provide a simple and convenient way of integrating user's workflow scripts with Serving API.",
    'long_description': "# Hydrosphere Serving SDK\n\n\n[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)\n[![PyPI version](https://badge.fury.io/py/hydrosdk.svg)](https://badge.fury.io/py/hydrosdk)\n\nThe package contains an implementation of [Hydroserving](https://github.com/Hydrospheredata/hydro-serving) API.\n\nThis package's purpose is to provide a simple and convenient way\nof integrating user's workflow scripts with Serving API.\n\nRead the full documentation [here](https://hydrospheredata.github.io/hydro-serving-sdk/).\n\n## Installation\n```\npip install hydrosdk\n```\n\n## Testing\nTested on python 3.6, 3.7, 3.8.\n\n1. `poetry install`\n2. `poetry run tox`\n\n\n",
    'author': 'Hydrospheredata',
    'author_email': None,
    'maintainer': 'Bulat Lutfullin',
    'maintainer_email': 'blutfullin@provectus.com',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
