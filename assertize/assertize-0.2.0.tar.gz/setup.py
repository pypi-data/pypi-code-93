# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['src']

package_data = \
{'': ['*']}

install_requires = \
['libcst']

entry_points = \
{'console_scripts': ['assertize = assertize:main']}

setup_kwargs = {
    'name': 'assertize',
    'version': '0.2.0',
    'description': 'Convert `self.assertSomething(...)` to `assert something`.',
    'long_description': None,
    'author': 'Stefane Fermigier',
    'author_email': 'sf@fermigier.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
