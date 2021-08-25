# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splunktalib',
 'splunktalib.common',
 'splunktalib.concurrent',
 'splunktalib.conf_manager',
 'splunktalib.schedule']

package_data = \
{'': ['*']}

install_requires = \
['defusedxml>=0,<1', 'httplib2>=0,<1', 'sortedcontainers>=2,<3']

setup_kwargs = {
    'name': 'splunktalib',
    'version': '2.1.1',
    'description': 'Supporting library for Splunk Add-ons',
    'long_description': None,
    'author': 'rfaircloth-splunk',
    'author_email': 'rfaircloth@splunk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/splunk/addonfactory-ta-library-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
