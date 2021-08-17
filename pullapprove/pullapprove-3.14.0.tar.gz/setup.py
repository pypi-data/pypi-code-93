# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pullapprove',
 'pullapprove.availability',
 'pullapprove.cli',
 'pullapprove.config',
 'pullapprove.context',
 'pullapprove.models',
 'pullapprove.models.base',
 'pullapprove.models.bitbucket',
 'pullapprove.models.github',
 'pullapprove.models.gitlab',
 'pullapprove.user_input']

package_data = \
{'': ['*']}

install_requires = \
['CacheControl[filecache]>=0.12.6,<0.13.0',
 'Jinja2>=3.0.1,<4.0.0',
 'PyJWT>=2.1.0,<3.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'cached-property>=1.5.2,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'cryptography>=3.4.7,<4.0.0',
 'dateparser>=1.0.0,<2.0.0',
 'marshmallow>=3.12.1,<4.0.0',
 'python-box>=5.3.0,<6.0.0',
 'requests>=2.25.1,<3.0.0',
 'wcmatch==8.2']

entry_points = \
{'console_scripts': ['pullapprove = pullapprove.cli:cli']}

setup_kwargs = {
    'name': 'pullapprove',
    'version': '3.14.0',
    'description': 'PullApprove is a framework for code review assignment, processes, and policies that integrates natively with your git host.',
    'long_description': '<a href="https://www.pullapprove.com/"><img src="https://www.pullapprove.com/static/img/logos/pull-approve-logo-gray-dk.png" alt="PullApprove" height="40px" /></a>\n---\n\nPullApprove is a framework for code review assignment, processes, and policies that integrates natively with your git host.\n\nThis repo contains some of the core models and configuration settings which are used by the [hosted service](https://www.pullapprove.com/).\n\nTo host your own version of PullApprove, please contact us at https://www.pullapprove.com/enterprise/.\n',
    'author': 'Dropseed',
    'author_email': 'python@dropseed.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.pullapprove.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
