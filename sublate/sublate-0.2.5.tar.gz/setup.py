# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['sublate']
install_requires = \
['Jinja2>=2.11.3,<3.0.0', 'PyYAML>=5.4.1,<6.0.0']

entry_points = \
{'console_scripts': ['sublate = sublate:main']}

setup_kwargs = {
    'name': 'sublate',
    'version': '0.2.5',
    'description': '',
    'long_description': None,
    'author': 'Jonathan Esposito',
    'author_email': 'hello@jontaylor.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
