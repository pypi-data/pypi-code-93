# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_fastx']

package_data = \
{'': ['*']}

install_requires = \
['flask-restx>=0.5.0,<0.6.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'flask-fastx',
    'version': '0.1.0',
    'description': 'Flask-Fastx is a Fast API style support for Flask. It Gives you MyPy types with the flexibility of flask.',
    'long_description': "==============\nFlask-Fastx\n==============\n\n.. image:: https://codecov.io/gh/tactful-ai/flask-faster-api/branch/main/graph/badge.svg?token=FZJANN69LH\n    :target: https://codecov.io/gh/tactful-ai/flask-faster-api\n    :alt: Code Coverage\n    \n.. image:: https://github.com/tactful-ai/flask-faster-api/actions/workflows/python-package.yml/badge.svg\n   :target: https://github.com/tactful-ai/flask-faster-api/actions/workflows/python-package.yml\n   :alt: CI Tests\n.. image:: https://img.shields.io/github/license/tactful-ai/flask-faster-api   \n    :alt: License\n.. image:: https://img.shields.io/github/stars/tactful-ai/flask-faster-api?style=social   :alt: GitHub Repo stars\n.. image:: https://img.shields.io/pypi/pyversions/flask-restx-square  \n    :target: https://pypi.org/project/flask-fastx\n    :alt: Supported Python versions\n   \n\nFlask-Fastx is a Fast API style support for Flask. It Gives you MyPy types with the flexibility of flask.\n\n\n\nCompatibility\n=============\n\nFlask-Fastx requires Python 3.7+. \n\n\n\nInstallation\n============\n\nYou can install Flask-Fastx with pip:\n\n.. code-block:: console\n\n    $ pip install flask-fastx\n    \n\nQuick start\n===========\n\nWith Flask-Fastx and the autowire decorator feature, parsing path parameters and creating api models is done using only one decorator! \n\nBefore Using Flask-Fastx\n================================\n\n.. image:: https://user-images.githubusercontent.com/63073172/130029969-2f59777d-3ad1-423f-bbf1-a8c73d056300.png\n\n\nAfter Using Flask-Fastx\n================================\n\n.. image:: https://user-images.githubusercontent.com/63073172/130017489-55b0d09d-5ba5-4455-8c88-29878b39e6c5.png\n\n\n\n\nContributors\n============\n\nFlask-Fastx is brought to you by @mfouad, @seifashraf1, @ahmedihabb2, @nadaabdelmaboud, @omargamal253\n\n\n\n\nContribution\n============\nWant to contribute? That's awesome! (Details Soon) \n",
    'author': 'nadaabdelmaboud     seifashraf1     ahmedihabb2     omargamal253',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/tactful-ai/flask-faster-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
