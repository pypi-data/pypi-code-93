# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ldict', 'ldict.abs', 'ldict.abs.mixin']

package_data = \
{'': ['*']}

install_requires = \
['garoupa>=2.210811.7,<3.0.0',
 'orjson>=3.5.0,<4.0.0',
 'uncompyle6>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'ldict',
    'version': '2.210815.2',
    'description': 'Lazy dict with universaly unique identified values',
    'long_description': '![test](https://github.com/davips/ldict/workflows/test/badge.svg)\n[![codecov](https://codecov.io/gh/davips/ldict/branch/main/graph/badge.svg)](https://codecov.io/gh/davips/ldict)\n\n# ldict\nUniquely identified lazy dict.\n\n[Latest version](https://github.com/davips/ldict)\n\n## Installation\n### as a standalone lib.\n```bash\n# Set up a virtualenv. \npython3 -m venv venv\nsource venv/bin/activate\n\n# Install from PyPI...\npip install --upgrade pip\npip install -U ldict\n\n# ...or, install from updated source code.\npip install git+https://github.com/davips/ldict\n```\n\n### from source\n```bash\ngit clone https://github.com/davips/ldict\ncd ldict\npoetry install\n```\n\n## Examples\n**Merging two ldicts**\n<details>\n<p>\n\n```python3\nfrom ldict import ldict\n\na = ldict(x=3)\nprint(a)\n"""\n{\n    "id": "000000000000000000000dCguKC6bS.95Bqe35gNJir04CxRv6dY1dPRO7R3PTKa",\n    "ids": "<1 hidden id>",\n    "x": 3\n}\n"""\n```\n\n```python3\n\nb = ldict(y=5)\nprint(b)\n"""\n{\n    "id": "000000000000000000000dlrfIktAZFYqwNrmOdFDZKV966TGLM7hu0fllFfC8Kt",\n    "ids": "<1 hidden id>",\n    "y": 5\n}\n"""\n```\n\n```python3\n\nprint(a + b)\n"""\n{\n    "id": "000000000000000000000aXHKqWzMQIMw6bFpTur11RVdIEJ9SLzyXQ57tuiIAfV",\n    "ids": "<1 hidden ids>",\n    "x": 3,\n    "y": 5\n}\n"""\n```\n\n\n</p>\n</details>\n\n## Features (current or planned)\n* [x] \n* [ ] \n\n## How to use [outdated]\nTwo main entities are identifiable: processing functions and bags of values.\nA processing function is any callable the follows the rules below.\nA bag of values is a ldict object. It is a mapping between string keys, called fields,\nand any serializable object.\nThe bag id (identifier) and the field ids are also part of the mapping.  \n\nThe user should provide a unique identifier for each function object.\nIt should be put as a 43 digits long base-62 string under the key "_id", or, \nalternatively, a Hosh object inside the returned dict, under the key "_id".\nThe only exception is when using the assignment syntax, \nbecause the return value is the proper result of the calculation.\nWhen using the assignment syntax, it is assumed the \'id\' should be automatically \ncalculated by the bytecode obtained through source code parsing.\nFor this reason, such functions should be simple, i.e., \nwith minimal external dependencies, to avoid the unfortunate situation where two\nfunctions with identical local code actually perform different calculations through\ncalls to external code that implement different algorithms with the same name.\n\nOne way to emulate such behavior for the function application syntax (a >> f) is to\nexplicitly refuse to provide a hash/id.\nThis can be done by setting `"_id": None` inside the returned dictionary.\n',
    'author': 'davips',
    'author_email': 'dpsabc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
