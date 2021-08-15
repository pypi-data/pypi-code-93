# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbcat', 'dbcat.catalog', 'dbcat.migrations', 'dbcat.migrations.versions']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML',
 'alembic>=1.6.5,<2.0.0',
 'amundsen-databuilder[athena,bigquery,glue,rds,snowflake]>=5.2.0,<6.0.0',
 'click',
 'psycopg2>=2.9.1,<3.0.0',
 'snowflake-sqlalchemy==1.2.4']

entry_points = \
{'console_scripts': ['dbcat = dbcat.__main__:main']}

setup_kwargs = {
    'name': 'dbcat',
    'version': '0.7.0',
    'description': 'Tokern Data Catalog',
    'long_description': '[![CircleCI](https://circleci.com/gh/tokern/dbcat.svg?style=svg)](https://circleci.com/gh/tokern/dbcat)\n[![codecov](https://codecov.io/gh/tokern/dbcat/branch/main/graph/badge.svg)](https://codecov.io/gh/tokern/dbcat)\n[![PyPI](https://img.shields.io/pypi/v/dbcat.svg)](https://pypi.python.org/pypi/dbcat)\n[![image](https://img.shields.io/pypi/l/dbcat.svg)](https://pypi.org/project/dbcat/)\n[![image](https://img.shields.io/pypi/pyversions/dbcat.svg)](https://pypi.org/project/dbcat/)\n\n# Data Catalog for Databases and Data Warehouses\n\n## Overview\n\n*dbcat* builds and maintains metadata from all your databases and data warehouses. \n*dbcat* is simple to use and maintain. Build a data catalog in minutes by providing\ncredentials using a command line application or API. Automate collection of metadata using\ncron or other workflow automation tools.\n\n*dbcat* stores the catalog in a Postgresql database. Use cloud hosting platforms to ease \noperations in maintaining the catalog in a Postgresql database. \n\nAccess the catalog using raw sql or the python APIs provided by *dbcat* in your python\napplication.\n\n## Quick Start\n\n*dbcat* is distributed as a python application.\n\n    python3 -m venv .env\n    source .env/bin/activate\n    pip install piicatcher\n\n    # configure the application\n    \n    dbcat -c <config dir> pull\n\n## Supported Technologies\n\nThe following databases are supported:\n\n* MySQL/Mariadb\n* PostgreSQL\n* AWS Redshift\n* BigQuery\n* Snowflake\n* AWS Glue\n\n',
    'author': 'Tokern',
    'author_email': 'info@tokern.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://tokern.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
