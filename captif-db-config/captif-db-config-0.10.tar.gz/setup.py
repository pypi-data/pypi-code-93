# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['captif_db_config']

package_data = \
{'': ['*']}

install_requires = \
['mysqlclient>=2.0.3,<3.0.0',
 'sqlalchemy-utils>=0.37.2,<0.38.0',
 'sqlalchemy>=1.4.15,<2.0.0']

setup_kwargs = {
    'name': 'captif-db-config',
    'version': '0.10',
    'description': '',
    'long_description': '# captif-db-config\n\nDatabase configuration.\n\n\n## Config file\n\nPlace a `.captif-db.ini` file in the home directory (`~` on linux). The config file should contain the following information:\n\n```\n[GENERAL]\nhost =\nport =\nusername = \npassword = \nssl_ca =\nssl_cert =\nssl_key =\n```\n',
    'author': 'John Bull',
    'author_email': 'john.bull@nzta.govt.nz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
