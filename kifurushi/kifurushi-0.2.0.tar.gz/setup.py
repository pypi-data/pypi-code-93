# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kifurushi', 'kifurushi.utils']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=20.3.0,<21.0.0']

setup_kwargs = {
    'name': 'kifurushi',
    'version': '0.2.0',
    'description': 'A simple library to forge network packets',
    'long_description': "# Kifurushi\n\n[![Pypi version](https://img.shields.io/pypi/v/kifurushi.svg)](https://pypi.org/project/kifurushi/)\n![](https://github.com/lewoudar/kifurushi/workflows/CI/badge.svg)\n[![Coverage Status](https://codecov.io/gh/lewoudar/kifurushi/branch/main/graphs/badge.svg?branch=main)](https://codecov.io/gh/lewoudar/kifurushi)\n[![Documentation Status](https://readthedocs.org/projects/kifurushi/badge/?version=latest)](https://kifurushi.readthedocs.io/en/latest/?badge=latest)\n[![License Apache 2](https://img.shields.io/hexpm/l/plug.svg)](http://www.apache.org/licenses/LICENSE-2.0)\n\nA simple library to forge network packets.\n\n## Why?\n\nI was playing with the DNS protocol using the excellent [scapy](https://scapy.readthedocs.io/) library.\nIt is very simple to forge network data with this library. I have always wondered why protocol libraries like\n[h2](https://hyper-h2.readthedocs.io/en/stable/) or [aioquic](https://aioquic.readthedocs.io/en/latest/) don't use it\nto forge packets instead of doing it all by hands and then I thought maybe it is because it will be overkill to import\nthe whole library containing many protocol implementations just for one thing you want to use (or maybe library authors\ndon't know the scapy library...). It would be glad to just use the scapy ability to forge packets without importing the\n**huge** protocol library. This is where the idea of *kifurushi* comes from.\n\nIt is a simple library that will help you forge network data quickly. It is less capable than scapy because its specific\ngoal is to implement a concrete protocol as opposed to scapy which makes it possible to give free rein to its imagination.\nSo if you find that your needs cannot be simply express with kifurushi, you probably need to use scapy.\n\n## Installation\n\nwith pip:\n\n```bash\npip install kifurushi\n```\n\nWith [poetry](https://python-poetry.org/docs/) an alternative package manager:\n\n```bash\npoetry add kifurushi\n```\n\nkifurushi starts working from **python3.6** and also supports **pypy3**. It has one dependency:\n* [attrs](https://www.attrs.org/en/stable/): A library helping to write classes without pain.\n\n## Documentation\n\nThe documentation is available at https://kifurushi.readthedocs.io\n\n## Usage\n\n```python\nimport socket\nimport enum\nfrom kifurushi import Packet, ShortField, ByteField, IntEnumField\n\nHOST = 'disney-stuff.com'\nPORT = 14006\n\n\nclass Mood(enum.Enum):\n  happy = 1\n  cool = 2\n  angry = 4\n\n\nclass Disney(Packet):\n  __fields__ = [\n    ShortField('mickey', 2),\n    ByteField('minnie', 3, hex=True),\n    IntEnumField('donald', 1, Mood)\n  ]\n\n\nwith socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:\n  disney = Disney()\n  s.connect((HOST, PORT))\n  disney.donald = Mood.cool.value\n  # we send the packet data\n  s.sendall(disney.raw)\n  # we create another packet object from raw bytes\n  received_packet = Disney.from_bytes(s.recv(1024))\n  print(received_packet)\n```\n\nTo see more protocol implementations check the folder [examples](examples) of the project.\n\n## Warnings\n\n* If you use the excellent [Pycharm](https://www.jetbrains.com/pycharm/) editor, you may notice weird warnings when\n  instantiating kifurushi fields. At the moment I'm writing this documentation, I'm using Pycharm 2020.3 and there is\n  an [issue](https://youtrack.jetbrains.com/issue/PY-46298) when subclassing **attrs** classes. So just ignore the\n  warning saying to fill the *format* parameter if you don't need it.\n* kifurushi is a young project, so it is expected to have breaking changes in the api without respecting the \n  [semver](https://semver.org/) principle. It is recommended to pin the version you are using for now.",
    'author': 'lewoudar',
    'author_email': 'lewoudar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://kifurushi.readthedocs.io/en/stable',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
