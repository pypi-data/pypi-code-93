# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['datareadingrequests']
install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'datareadingrequests',
    'version': '1.0.0',
    'description': "A client for Energize Andover's Building Energy API, with a focus on clarity and usability.",
    'long_description': None,
    'author': 'fisher',
    'author_email': 'fisher521.fs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
