# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sundial']

package_data = \
{'': ['*']}

install_requires = \
['archimedes-python-client>=2.2.4,<3.0.0',
 'boto3>=1.17.99,<2.0.0',
 'click==7.1.2',
 'coverage>=5.5,<6.0',
 'dash>=1.20.0,<2.0.0',
 'flake8>=3.9.2,<4.0.0',
 'holidays>=0.11.1,<0.12.0',
 'icecream>=2.1.1,<3.0.0',
 'mlflow>=1.18.0,<2.0.0',
 'notebook>=6.4.0,<7.0.0',
 'pandas>=1.2.5,<2.0.0',
 'pytest>=6.2.4,<7.0.0',
 'python-dotenv>=0.18.0,<0.19.0',
 'sklearn>=0.0,<0.1',
 'streamlit>=0.83.0,<0.84.0',
 'tensorflow==2.2.0']

setup_kwargs = {
    'name': 'sundial-framework',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Gavin Bell',
    'author_email': 'gavin.bell@optimeering.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
