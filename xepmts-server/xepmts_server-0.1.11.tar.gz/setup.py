# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tests',
 'xepmts_server',
 'xepmts_server.admin',
 'xepmts_server.sc',
 'xepmts_server.v1',
 'xepmts_server.v2',
 'xepmts_server.versions']

package_data = \
{'': ['*']}

install_requires = \
['Eve-Swagger>=0.1.3,<0.2.0',
 'Eve>=1.1.5,<2.0.0',
 'eve-healthcheck>=0.3.1,<0.4.0',
 'eve-jwt>=0.1.9,<0.2.0',
 'flask_swagger_ui>=3.36.0,<4.0.0',
 'prometheus_flask_exporter>=0.18.1,<0.19.0',
 'toml>=0.10.2,<0.11.0',
 'xeauth==0.1.2',
 'xepmts-endpoints>=0.1.0,<0.2.0']

entry_points = \
{'console_scripts': ['xepmts-server = xepmts_server.cli:main']}

setup_kwargs = {
    'name': 'xepmts-server',
    'version': '0.1.11',
    'description': 'Top-level package for xepmts-server.',
    'long_description': '=============\nxepmts-server\n=============\n\n\n.. image:: https://img.shields.io/pypi/v/xepmts_server.svg\n        :target: https://pypi.python.org/pypi/xepmts_server\n\n.. image:: https://img.shields.io/travis/jmosbacher/xepmts_server.svg\n        :target: https://travis-ci.com/jmosbacher/xepmts_server\n\n.. image:: https://readthedocs.org/projects/xepmts-server/badge/?version=latest\n        :target: https://xepmts-server.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n\n\n\n\nServer for the xepmts api\n\n\n* Free software: MIT\n* Documentation: https://xepmts-server.readthedocs.io.\n\n\nFeatures\n--------\n\n* TODO\n\nCredits\n-------\n\nThis package was created with Cookiecutter_ and the `briggySmalls/cookiecutter-pypackage`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`briggySmalls/cookiecutter-pypackage`: https://github.com/briggySmalls/cookiecutter-pypackage\n',
    'author': 'Yossi Mosbacher',
    'author_email': 'joe.mosbacher@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jmosbacher/xepmts_server',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1',
}


setup(**setup_kwargs)
