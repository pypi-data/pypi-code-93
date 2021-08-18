# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['peeringdb', 'peeringdb._debug', 'peeringdb.output']

package_data = \
{'': ['*']}

install_requires = \
['confu>=1,<2', 'munge>=1,<2', 'twentyc.rpc>=1,<2']

entry_points = \
{'console_scripts': ['peeringdb = peeringdb.cli:main'],
 'markdown.extensions': ['pymdgen = pymdgen.md:Extension']}

setup_kwargs = {
    'name': 'peeringdb',
    'version': '1.2.1',
    'description': 'PeeringDB Django models',
    'long_description': '# peeringdb-py\n\n[![PyPI](https://img.shields.io/pypi/v/peeringdb.svg?maxAge=3600)](https://pypi.python.org/pypi/peeringdb)\n[![Travis CI](https://img.shields.io/travis/peeringdb/peeringdb-py.svg?maxAge=3600)](https://travis-ci.org/peeringdb/peeringdb-py)\n[![Codecov](https://img.shields.io/codecov/c/github/peeringdb/peeringdb-py/master.svg?maxAge=3600)](https://codecov.io/github/peeringdb/peeringdb-py)\n\nPeeringDB python client\n\nSee http://peeringdb.github.io/peeringdb-py/ for docs\n',
    'author': 'PeeringDB',
    'author_email': 'support@peeringdb.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/peeringdb/peeringdb-py',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
