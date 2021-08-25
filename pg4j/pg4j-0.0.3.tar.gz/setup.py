# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pg4j', 'pg4j.cli']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'SQLAlchemy>=1.4.22,<2.0.0',
 'pre-commit>=2.14.0,<3.0.0',
 'psycopg2-binary>=2.9.1,<3.0.0',
 'pydantic[dotenv]>=1.8.2,<2.0.0',
 'typer>=0.3.2,<0.4.0',
 'types-PyYAML>=5.4.6,<6.0.0']

extras_require = \
{'docs': ['markdown-include==0.6.0',
          'mkdocs>=1.1.2,<2.0.0',
          'mkdocs-autorefs>=0.1.1,<0.2.0',
          'mkdocs-markdownextradata-plugin>=0.2.4,<0.3.0',
          'mkdocs-material>=7.0.6,<8.0.0',
          'mkdocstrings>=0.15.0,<0.16.0',
          'pdocs[docs]>=1.1.1,<2.0.0',
          'pymdown-extensions>=8.2,<9.0']}

entry_points = \
{'console_scripts': ['pg4j = pg4j.__main__:app']}

setup_kwargs = {
    'name': 'pg4j',
    'version': '0.0.3',
    'description': 'A package designed to perform etl from a postgres database to a neo4j database.',
    'long_description': None,
    'author': 'Michael Statt',
    'author_email': 'michael.statt@modelyst.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
