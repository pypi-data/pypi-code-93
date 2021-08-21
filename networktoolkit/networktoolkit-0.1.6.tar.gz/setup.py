# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['networktoolkit']

package_data = \
{'': ['*']}

install_requires = \
['Click>=7.0,<8.0',
 'cryptography>=3.4.7,<4.0.0',
 'requests>=2.23.0,<3.0.0',
 'scapy>=2.4.3,<3.0.0']

extras_require = \
{'docs': ['sphinx>=3,<4']}

entry_points = \
{'console_scripts': ['arpspoof = networktoolkit.arpspoof:cli',
                     'netwatch = networktoolkit.netwatch:cli',
                     'networkscan = networktoolkit.networkscan:cli',
                     'portuselookup = networktoolkit.portuselookup:cli',
                     'showhosts = networktoolkit.showhosts:cli',
                     'vendorlookup = networktoolkit.vendorlookup:cli']}

setup_kwargs = {
    'name': 'networktoolkit',
    'version': '0.1.6',
    'description': 'A collection of networking tools',
    'long_description': '# Network Toolkit\n\nA collection of networking tools\n\n\n## Installation\n\nYou can install networktookit from pypi.\nThis requires you to have python3.8 installed.\n\n```bash\npython -m pip install --upgrade networktoolkit\n```\n\n## Usage\n\nThe project contain many tools.\n\nThe current tools are:\n\n* `vendorlookup` - check the vendor of a macaddress\n* `portuselookup` - checks to see if a given port is allocated to any particular service\n* `networkscan` - allows you to scan a given ip range and returns a list of all ips (with mac addresses and vendors) in the given range that are accessable on the network\n* `arpspoof` - allows you to spoof a given ip address by sending ARP responses\n\nEach of these has its own help page.\nAs an example, you can assess the help for `arpspoof` like this:\n\n```bash\narpspoof --help\n```\n\n\n## About\n\nThis project uses [scapy](https://scapy.net/) for generating and sending network packets, and [click](https://click.palletsprojects.com) to give each python script a command line interface.\n\n## Contributing\n\nFeel free to contribute to this project by opening a merge request.\nI would request that all contributed code is pep8 complient.\n\n## Issues\n\nIf anything is broke, you have a usage question, or a feature suggestion feel free to create an issue on github.\n\n\n',
    'author': 'Luke Spademan',
    'author_email': 'info@lukespademan.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mokytis/networktoolkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
