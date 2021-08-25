# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['djangofobi_email_router']

package_data = \
{'': ['*'],
 'djangofobi_email_router': ['locale/fr/LC_MESSAGES/*',
                             'templates/email_router/*']}

install_requires = \
['Django>=1.11', 'django-fobi>=0.17.0,<0.18.0']

setup_kwargs = {
    'name': 'djangofobi-email-router',
    'version': '1.0.1',
    'description': 'A django-fobi handler plugin to send the content of a form to different e-mails addresses, depending on a value of a form field.',
    'long_description': None,
    'author': 'KAPT dev team',
    'author_email': 'dev@kapt.mobi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
