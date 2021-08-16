# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_dragonpay_py3',
 'django_dragonpay_py3.api',
 'django_dragonpay_py3.migrations']

package_data = \
{'': ['*'], 'django_dragonpay_py3': ['templates/dragonpay_soapxml/*']}

install_requires = \
['lxml>=4.6.3,<5.0.0', 'pycrypto>=2.6.1,<3.0.0']

setup_kwargs = {
    'name': 'django-dragonpay-py3',
    'version': '0.1.3',
    'description': '',
    'long_description': None,
    'author': 'Cymmer John Maranga',
    'author_email': 'cymmer4@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
