# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['panel_auth0_oidc', 'tests']

package_data = \
{'': ['*']}

install_requires = \
['panel']

entry_points = \
{'panel.auth': ['auth0_oidc = '
                'panel_auth0_oidc.panel_auth0_oidc:OidcAuth0Handler']}

setup_kwargs = {
    'name': 'panel-auth0-oidc',
    'version': '0.1.2',
    'description': 'Top-level package for Panel Auth0 Oidc.',
    'long_description': '================\nPanel Auth0 Oidc\n================\n\n\n.. image:: https://img.shields.io/pypi/v/panel_auth0_oidc.svg\n        :target: https://pypi.python.org/pypi/panel_auth0_oidc\n\n.. image:: https://img.shields.io/travis/jmosbacher/panel_auth0_oidc.svg\n        :target: https://travis-ci.com/jmosbacher/panel_auth0_oidc\n\n.. image:: https://readthedocs.org/projects/panel-auth0-oidc/badge/?version=latest\n        :target: https://panel-auth0-oidc.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n\n\n\n\nOidc Auth0 oauth plugin for panel\n\n\n* Free software: MIT\n* Documentation: https://panel-auth0-oidc.readthedocs.io.\n\n\nFeatures\n--------\n\n* TODO\n\nCredits\n-------\n\nThis package was created with Cookiecutter_ and the `briggySmalls/cookiecutter-pypackage`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`briggySmalls/cookiecutter-pypackage`: https://github.com/briggySmalls/cookiecutter-pypackage\n',
    'author': 'Yossi Mosbacher',
    'author_email': 'joe.mosbacher@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jmosbacher/panel_auth0_oidc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
