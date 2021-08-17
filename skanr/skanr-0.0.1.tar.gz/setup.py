# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skanr']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0', 'ipaddress>=1.0.23,<2.0.0']

entry_points = \
{'console_scripts': ['skanr = skanr.cli:main']}

setup_kwargs = {
    'name': 'skanr',
    'version': '0.0.1',
    'description': 'Multithreaded IPV4 port scanner written in python',
    'long_description': '# skanr\n\nMultithreaded network port scanner for IPV4 addresses\n\n## requirements\n\n1. known Target host IP Address\n\n## installation\n\n`pip install skanr`\n\n## usage\n\n### Help\n\nDisplay the help\n\n```\nskanr -h\nusage: skanr [-h] [-s] [-e] [-t] [--version] target_ip\n\nPerform a network port scan of a host IP address\n\npositional arguments:\n  target_ip          Target IP address (xxx.xxx.xxx.xxx)\n\noptional arguments:\n  -h, --help         show this help message and exit\n  -s , --startport   Port number to start scanning (default: 1)\n  -e , --endport     End port number of scan range (default: 1024, max: 65535)\n  -t , --threads     number of scan threads to run (default: 32, max: 1024)\n  --version          prints version information\n```\n\n### basic IP scan\n\nwill scan an IP address from ports 1-1024 using 32 threads\n\n```\nskanr 10.37.129.9\n\nskanr v 0.0.1\nScanning IP: 10.37.129.9 ports: 1 - 1024 threads: 32\n-=================================================================-\nport 21 :open\nport 23 :open\nport 22 :open\nport 53 :open\nport 80 :open\nport 110 :open\nport 111 :open\nport 139 :open\nport 143 :open\nport 445 :open\nport 901 :open\n```\n\n### scan port range on target\n\nTo scan a port range on the target machine use `-s` and `-e` to specify the start and end ports\n\nif no start ot end prot is given then defaults apply\n\n```\nskanr 10.37.129.9 -s 20 -e 100\n\nskanr v 0.0.1\nScanning IP: 10.37.129.9 ports: 20 - 100 threads: 32\n-=================================================================-\nport 21 :open\nport 22 :open\nport 23 :open\nport 53 :open\nport 80 :open\n```\n\n### specifing threads\n\nTo speed up the port scanning the number of threads can be passed using the `-t` argument up to a max of 1024 threads, to prevent starting unwanted threads, the number of threads started will never be greater than the number of ports to be scanned. \n\n```\nskanr 10.37.129.9 -e 65535 -t 1024\n\nskanr v 0.0.1\nScanning IP: 10.37.129.9 ports: 1 - 65535 threads: 1024\n-=================================================================-\nport 21 :open\nport 22 :open\nport 23 :open\nport 53 :open\nport 80 :open\nport 110 :open\nport 111 :open\nport 139 :open\nport 143 :open\nport 445 :open\nport 901 :open\nport 2049 :open\nport 6665 :open\nport 6666 :open\nport 6669 :open\nport 6667 :open\nport 6668 :open\nport 8787 :open\nport 37159 :open\nport 44180 :open\nport 50166 :open\n```\n',
    'author': 'Stephen Eaton',
    'author_email': 'seaton@strobotics.com.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/madeinoz67/skan',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
