# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['anyioc']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'anyioc',
    'version': '0.12.0',
    'description': '',
    'long_description': "# anyioc\n\n![GitHub](https://img.shields.io/github/license/Cologler/anyioc-python.svg)\n[![Build Status](https://travis-ci.com/Cologler/anyioc-python.svg?branch=master)](https://travis-ci.com/Cologler/anyioc-python)\n[![PyPI](https://img.shields.io/pypi/v/anyioc.svg)](https://pypi.org/project/anyioc/)\n\nAnother simple ioc framework for python.\n\n## Usage\n\n``` py\nfrom anyioc import ServiceProvider\nprovider = ServiceProvider()\nprovider.register_singleton('the key', lambda ioc: 102) # ioc will be a `IServiceProvider`\nvalue = provider.get('the key')\nassert value == 102\n```\n\n## Register and resolve\n\nBy default, you can use following methods to register services:\n\n- `ServiceProvider.register_singleton(key, factory)`\n- `ServiceProvider.register_scoped(key, factory)`\n- `ServiceProvider.register_transient(key, factory)`\n- `ServiceProvider.register(key, factory, lifetime)`\n- `ServiceProvider.register_value(key, value)`\n- `ServiceProvider.register_group(key, keys)`\n- `ServiceProvider.register_bind(new_key, target_key)`\n\nAnd use following methods to resolve services:\n\n- `ServiceProvider.__getitem__(key)`\n- `ServiceProvider.get(key)`\n- `ServiceProvider.get_many(key)`\n\n*`get` return `None` if the service was not found, but `__getitem__` will raise a `ServiceNotFoundError`.*\n\nRead full [documentation](https://github.com/Cologler/anyioc-python/wiki).\n",
    'author': 'Cologler',
    'author_email': 'skyoflw@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
