# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['linkedin_matrix',
 'linkedin_matrix.commands',
 'linkedin_matrix.db',
 'linkedin_matrix.db.upgrade',
 'linkedin_matrix.formatter',
 'linkedin_matrix.web']

package_data = \
{'': ['*']}

install_requires = \
['asyncpg>=0.23.0',
 'commonmark>=0.9.1,<0.10.0',
 'linkedin-messaging>=0.4.3,<0.5.0',
 'mautrix>=0.10.3,<0.11.0',
 'python-magic>=0.4.24,<0.5.0',
 'ruamel.yaml>=0.17.0,<0.18.0']

extras_require = \
{'e2be': ['pycryptodome>=3.10.1,<4.0.0',
          'python-olm',
          'unpaddedbase64>=2.1.0,<3.0.0'],
 'images': ['Pillow>=8.3.1,<9.0.0'],
 'metrics': ['prometheus-client>=0.11.0,<0.12.0']}

setup_kwargs = {
    'name': 'linkedin-matrix',
    'version': '0.5.0',
    'description': 'A Matrix-LinkedIn Messages puppeting bridge.',
    'long_description': '# linkedin-matrix\n\n[![pipeline status](https://gitlab.com/beeper/linkedin-matrix/badges/master/pipeline.svg)](https://gitlab.com/beeper/linkedin-matrix/-/commits/master) \n[![Matrix Chat](https://img.shields.io/matrix/linkedin-matrix:nevarro.space?server_fqdn=matrix.nevarro.space)](https://matrix.to/#/#linkedin-matrix:nevarro.space?via=nevarro.space&via=sumnerevans.com)\n[![Apache 2.0](https://img.shields.io/github/license/sumnerevans/linkedin-matrix)](https://github.com/sumnerevans/linkedin-matrix/blob/master/LICENSE)\n\nLinkedIn Messaging <-> Matrix bridge built using\n[mautrix-python](https://github.com/tulir/mautrix-python) and\n[linkedin-messaging-api](https://github.com/sumnerevans/linkedin-messaging-api).\n\n## Documentation\n\nNot much yet :)\n\nIt is a Poetry project that requires Python 3.9+, PostgreSQL. Theoretically, all\nyou need to do is:\n\n1. Copy the `linkedin_matrix/example-config.yaml` file and modify it to your\n   needs.\n\n2. Install the dependencies with Poetry:\n\n   ```\n   $ poetry install\n   ```\n\n   and activate the virtualenv.\n\n3. Generate the registration file\n\n   ```\n   $ python -m linkedin_matrix -g\n   ```\n\n   and add it to your Synapse config.\n\n4. Run the bridge using:\n\n   ```\n   $ python -m linkedin_matrix\n   ```\n\n### Features & Roadmap\n[ROADMAP.md](https://github.com/sumnerevans/linkedin-matrix/blob/master/ROADMAP.md)\ncontains a general overview of what is supported by the bridge.\n\n## Discussion\n\nMatrix room:\n[`#linkedin-matrix:nevarro.space`](https://matrix.to/#/#linkedin-matrix:nevarro.space?via=nevarro.space&via=sumnerevans.com)\n',
    'author': 'Sumner Evans',
    'author_email': 'inquiries@sumnerevans.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sumnerevans/linkedin-matrix',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
