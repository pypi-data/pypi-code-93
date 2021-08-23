# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['prjforinfcreditvilfw']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.15.18,<2.0.0',
 'cython>=0.29.20,<0.30.0',
 'matplotlib>=3.2.1,<4.0.0',
 'numba>=0.50.1,<0.51.0',
 'numpy>=1.18.5,<2.0.0',
 'python-frontmatter>=0.5.0,<0.6.0',
 'pyyaml>=5.3.1,<6.0.0',
 'scipy>=1.4.1,<2.0.0',
 'seaborn>=0.10.1,<0.11.0',
 'sklearn>=0.0,<0.1',
 'statsmodels>=0.11.1,<0.12.0',
 'urllib3>=1.25.10,<2.0.0']

setup_kwargs = {
    'name': 'prjforinfcreditvilfw',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Fan Wang',
    'author_email': 'wangfanbsg75@live.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
