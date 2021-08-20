# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['onionshare_cli', 'onionshare_cli.web']

package_data = \
{'': ['*'],
 'onionshare_cli': ['resources/*',
                    'resources/static/css/*',
                    'resources/static/img/*',
                    'resources/static/js/*',
                    'resources/templates/*']}

install_requires = \
['click',
 'colorama',
 'eventlet',
 'flask-httpauth',
 'flask-socketio==5.0.1',
 'flask==1.1.4',
 'psutil',
 'pycryptodome',
 'pysocks',
 'requests[socks]',
 'setuptools',
 'stem',
 'unidecode',
 'urllib3']

entry_points = \
{'console_scripts': ['onionshare-cli = onionshare_cli:main']}

setup_kwargs = {
    'name': 'onionshare-cli',
    'version': '2.3.3',
    'description': 'OnionShare lets you securely and anonymously send and receive files. It works by starting a web server, making it accessible as a Tor onion service, and generating an unguessable web address so others can download files from you, or upload files to you. It does _not_ require setting up a separate server or using a third party file-sharing service.',
    'long_description': None,
    'author': 'Micah Lee',
    'author_email': 'micah@micahflee.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
