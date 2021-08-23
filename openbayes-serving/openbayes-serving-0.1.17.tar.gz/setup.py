# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openbayes_serving',
 'openbayes_serving.debug',
 'openbayes_serving.parts',
 'openbayes_serving.utils']

package_data = \
{'': ['*'], 'openbayes_serving.debug': ['static/*']}

install_requires = \
['Flask-Cors',
 'accept-types',
 'flask',
 'httptools',
 'msgpack>1.0.0',
 'pprintpp',
 'requests',
 'uvicorn',
 'uvloop']

setup_kwargs = {
    'name': 'openbayes-serving',
    'version': '0.1.17',
    'description': 'Framework for Openbayes Serving',
    'long_description': None,
    'author': 'Proton',
    'author_email': 'bwang@openbayes.com',
    'maintainer': 'Proton',
    'maintainer_email': 'bwang@openbayes.com',
    'url': 'https://openbayes.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
