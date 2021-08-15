# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

modules = \
['sqlalchemy_events']
install_requires = \
['SQLAlchemy>=1.4.22,<2.0.0']

setup_kwargs = {
    'name': 'sqlalchemy-events',
    'version': '0.1.0',
    'description': 'Helper for SQLAlchemy Events',
    'long_description': '# sqlalchemy-events\nHelper for handling sqlalchemy events\n',
    'author': 'Ngalim Siregar',
    'author_email': 'ngalim.siregar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nsiregar/sqlalchemy-events',
    'package_dir': package_dir,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
