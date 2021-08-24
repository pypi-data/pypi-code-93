# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sphinx_scylladb_theme',
 'sphinx_scylladb_theme.extensions',
 'sphinx_scylladb_theme.lexers']

package_data = \
{'': ['*'],
 'sphinx_scylladb_theme': ['static/css/*',
                           'static/img/*',
                           'static/img/icons/*',
                           'static/img/mascots/*',
                           'static/js/*']}

install_requires = \
['Sphinx>=2.4.4,<3.0.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'pyyaml>=5.3,<6.0',
 'recommonmark==0.5.0',
 'sphinx-copybutton>=0.2.8,<0.3.0',
 'sphinx-multiversion-scylla>=0.2.4,<0.3.0',
 'sphinx-notfound-page>=0.6,<0.7',
 'sphinx-tabs>=3.1.0,<4.0.0']

setup_kwargs = {
    'name': 'sphinx-scylladb-theme',
    'version': '1.0.1',
    'description': 'A Sphinx Theme for ScyllaDB documentation projects',
    'long_description': '===================\nScylla Sphinx Theme\n===================\n\nSphinx theme for Scylla documentation projects.\n\n`Read More: <https://github.com/scylladb/sphinx-scylladb-theme>`_\n',
    'author': 'David García',
    'author_email': 'hi@davidgarcia.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
