# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sniff']

package_data = \
{'': ['*']}

install_requires = \
['Cython>=0.29.24,<0.30.0', 'dpkt>=1.9.6,<2.0.0']

setup_kwargs = {
    'name': 'libsniffpy',
    'version': '0.3.0',
    'description': 'A python3 wrapper around libsniff',
    'long_description': '# libsniffpy\n\n![libsniff.png](https://raw.githubusercontent.com/4thel00z/logos/master/libsniff.png)\n\n## Motivation\n\nI wanted to have a nice cython/python wrapper around [libsniff](https://github.com/4thel00z/libsniff).\nThis name might confuse you, I just care about sniffing wifi packets from a nic in monitor mode.\n\n## Installation\n\n```\npip install libsniffpy\n```\n\n## Usage\n\n```python\n\nfrom sniff import get_socket\n\n# You might have to adjust \ns = get_socket("wlan0mon")\n# or whatever big number, forgot how big those frames are lel\npkg = s.recv(3000)\n# do some parsing magic, out of scope for this package\n```\n\n## Guidance for n00bs\n\nThis lib opens a raw socket for a monitor mode enabled interface.\nIt needs privs that your user probably don\'t have.\n\nEither you run this stuff as `root` or you do sth like this:\n\n```\nsudo setcap cap_net_raw,cap_net_admin=eip\n```\n\non a wrapper script that calls your python interpreter.\n\n## License\n\nThis project is licensed under the GPL-3 license.\n',
    'author': '4thel00z',
    'author_email': '4thel00z@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/4thel00z/libsniffpy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
