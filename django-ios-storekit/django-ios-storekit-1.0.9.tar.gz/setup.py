# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['storekit', 'storekit.migrations']

package_data = \
{'': ['*']}

install_requires = \
['Django>=2,<3', 'requests>=2,<3']

setup_kwargs = {
    'name': 'django-ios-storekit',
    'version': '1.0.9',
    'description': "iOS In-App Purchase's receipt validation server plugin for Django",
    'long_description': "# django-ios-storekit\n\n[![Tests](https://github.com/nnsnodnb/django-ios-storekit/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/nnsnodnb/django-ios-storekit/actions/workflows/tests.yml)\n[![Linter](https://github.com/nnsnodnb/django-ios-storekit/actions/workflows/linter.yml/badge.svg?branch=master)](https://github.com/nnsnodnb/django-ios-storekit/actions/workflows/linter.yml)\n[![Coverage Status](https://coveralls.io/repos/github/nnsnodnb/django-ios-storekit/badge.svg?branch=master)](https://coveralls.io/github/nnsnodnb/django-ios-storekit?branch=master)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-ios-storekit)\n![PyPI](https://img.shields.io/pypi/v/django-ios-storekit)\n![PyPI - Format](https://img.shields.io/pypi/format/django-ios-storekit)\n![PyPI - Wheel](https://img.shields.io/pypi/wheel/django-ios-storekit)\n\nA Django plugin for iOS StoreKit server.\n\n## Supported python versions\n\n3.6.x ~ 3.8.x\n\n## Supported django versions\n\n2.x\n\n## Installation\n\n```shell script\n$ pip install django-ios-storekit\n```\n\nAdd `storekit` into `INSTALLED_APPS` in `settings.py` file.\n\n```python\nINSTALLED_APPS += (\n    'storekit',\n)\n```\n\n```shell script\n$ python manage.py migrate\n```\n\n## License\n\nThis software is licensed under the MIT License (See [LICENSE](https://github.com/nnsnodnb/django-ios-storekit/blob/master/LICENSE)).\n",
    'author': 'Yuya Oka',
    'author_email': 'nnsnodnb@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nnsnodnb/django-ios-storekit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
