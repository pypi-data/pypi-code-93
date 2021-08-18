# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['salesman',
 'salesman.admin',
 'salesman.admin.migrations',
 'salesman.basket',
 'salesman.basket.migrations',
 'salesman.checkout',
 'salesman.core',
 'salesman.orders',
 'salesman.orders.migrations']

package_data = \
{'': ['*'],
 'salesman.admin': ['static/salesman/admin/*',
                    'templates/salesman/admin/*',
                    'templates/salesman/admin/includes/*']}

install_requires = \
['django>=3.0,<3.3', 'djangorestframework>=3.11,<3.13']

extras_require = \
{'docs': ['wagtail>=2.9,<2.15',
          'sphinx>=4.0,<4.1',
          'sphinx-rtd-theme>=0.5,<0.6',
          'sphinx-autobuild>=2021.3,<2021.4',
          'sphinxcontrib-httpdomain>=1.7,<1.8'],
 'example': ['Pygments>=2.6,<3.0', 'wagtail>=2.9,<2.15'],
 'pygments': ['Pygments>=2.6,<3.0'],
 'tests': ['Pygments>=2.6,<3.0',
           'wagtail>=2.9,<2.15',
           'pytest>=6.2,<6.3',
           'pytest-django>=4.2,<4.3',
           'pytest-cov>=2.11,<2.12']}

setup_kwargs = {
    'name': 'django-salesman',
    'version': '1.0.3',
    'description': 'Headless e-commerce framework for Django.',
    'long_description': '<p align="center">\n    <a href="https://django-salesman.readthedocs.org/">\n        <img src="https://cdn.jsdelivr.net/gh/dinoperovic/django-salesman@master/docs/_static/logo.svg" width="250" alt="Salesman logo">\n    </a>\n</p>\n<h3 align="center">Headless e-commerce framework for Django.</h3>\n<p align="center">\n    <a href="https://pypi.org/project/django-salesman/">\n        <img alt="PyPI" src="https://img.shields.io/pypi/v/django-salesman">\n    </a>\n    <a href="https://github.com/dinoperovic/django-salesman/actions?query=workflow:Test">\n        <img alt="GitHub Workflow Status (branch)" src="https://img.shields.io/github/workflow/status/dinoperovic/django-salesman/Test/master">\n    </a>\n    <a href="http://codecov.io/github/dinoperovic/django-salesman">\n        <img alt="Codecov branch" src="https://img.shields.io/codecov/c/github/dinoperovic/django-salesman/master">\n    </a>\n    <a href="https://pypi.org/project/django-salesman/">\n        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/django-salesman">\n    </a>\n    <a href="https://pypi.org/project/django-salesman/">\n        <img alt="PyPI - Django Version" src="https://img.shields.io/pypi/djversions/django-salesman">\n    </a>\n    <a href="https://github.com/psf/black">\n        <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">\n    </a>\n</p>\n\n**Salesman** provides a configurable system for building an online store.\nIt includes a **RESTful** API with endpoints for manipulating the basket,\nprocessing the checkout and payment operations as well as managing customer orders.\n\n## Features\n\n- API endpoints for **Basket**, **Checkout** and **Order**\n- Support for as many **Product** types needed using generic relations\n- Pluggable **Modifier** system for basket processing\n- **Payment** methods interface to support any gateway necessary\n- Customizable **Order** model\n- [Wagtail](https://wagtail.io/) and **Django** admin implementation\n\n## Documentation\n\nDocumentation is available on [Read the Docs](https://django-salesman.readthedocs.org).\n\n<p>\n    <a href="https://www.buymeacoffee.com/dinoperovic">\n        <img src="https://cdn.jsdelivr.net/gh/dinoperovic/django-salesman@master/docs/_static/buymeacoffee.svg" alt="Buy me a coffee">\n    </a>\n</p>\n',
    'author': 'Dino Perovic',
    'author_email': 'dino.perovic@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/django-salesman/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
