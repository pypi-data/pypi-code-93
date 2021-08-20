# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aurorae',
 'aurorae.cnab240',
 'aurorae.cnab240.v10_7',
 'aurorae.payroll',
 'aurorae.providers',
 'aurorae.providers.api',
 'aurorae.providers.spreadsheet']

package_data = \
{'': ['*'], 'aurorae': ['sample/*', 'staticfiles/*']}

install_requires = \
['Pygments>=2.9.0,<3.0.0',
 'attrs>=21.2.0,<22.0.0',
 'backcall>=0.2.0,<0.3.0',
 'decorator>=5.0.9,<6.0.0',
 'et-xmlfile>=1.1.0,<2.0.0',
 'fastapi>=0.68.0,<0.69.0',
 'iniconfig>=1.1.1,<2.0.0',
 'ipython>=7.25.0,<8.0.0',
 'ipython_genutils>=0.2.0,<0.3.0',
 'jedi>=0.18.0,<0.19.0',
 'openpyxl>=3.0.7,<4.0.0',
 'packaging>=21.0,<22.0',
 'parso>=0.8.2,<0.9.0',
 'pexpect>=4.8.0,<5.0.0',
 'pickleshare>=0.7.5,<0.8.0',
 'pluggy>=0.13.1,<0.14.0',
 'prompt-toolkit>=3.0.19,<4.0.0',
 'ptyprocess>=0.7.0,<0.8.0',
 'py>=1.10.0,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pyparsing>=2.4.7,<3.0.0',
 'requests>=2.26.0,<3.0.0',
 'toml>=0.10.2,<0.11.0',
 'traitlets>=5.0.5,<6.0.0',
 'uvicorn[standard]>=0.15.0,<0.16.0',
 'wcwidth>=0.2.5,<0.3.0']

entry_points = \
{'console_scripts': ['generate_cnab = '
                     'aurorae.cnab240.writer:generate_cnab_files',
                     'generate_cnab_sample = '
                     'aurorae.cnab240.writer:generate_cnab_sample']}

setup_kwargs = {
    'name': 'aurorae',
    'version': '0.0.2',
    'description': 'A Python implementation of the CNAB240 file to perform bulk payments.',
    'long_description': '# aurorae\n\n[![PyPi version](https://img.shields.io/pypi/v/aurorae.svg)](https://pypi.python.org/pypi/aurorae)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/aurorae)](https://pypi.org/project/aurorae/)\n[![CI](https://github.com/vintasoftware/aurorae/actions/workflows/actions.yaml/badge.svg)](https://github.com/vintasoftware/aurorae/actions/workflows/actions.yaml)\n[![Coverage Status](https://coveralls.io/repos/github/vintasoftware/aurorae/badge.svg?branch=main)](https://coveralls.io/github/vintasoftware/aurorae?branch=main)\n[![Documentation Status](https://readthedocs.org/projects/aurorae/badge/?version=latest)](https://aurorae.readthedocs.io/en/latest/?badge=latest)\n[![License: MIT](https://img.shields.io/github/license/vintasoftware/django-react-boilerplate.svg)](LICENSE.txt)\n\n**aurorae** is a tool to generate fixed-width CNAB240 files to perform bulk payments.\n\n### aurorae _does..._\n- Generates CNAB240 files for bulk payments\n- Allows easy extension of different types of input files\n\n### aurorae _does not..._\n- Address charge or as Brazilian banks call "cobrança"\n- Address payments by PIX, we only support payments through bank information\n\nBut, pull requests are welcomed.\n\n## How It Works\n**aurorae** uses Python type hinting for data validation and generation of fixed-width CNAB 240 files. The library receives as inputs an spreadsheet that must be a match of the Pydantic model [Spreadsheet](https://github.com/vintasoftware/aurorae/blob/main/aurorae/providers/spreadsheet/models.py), a general handler parses the initial data to an intermediary representation used by the CNAB240 module to generate files. Different types of inputs are supported by library through the creation of new providers, check the [spreadsheet provider](https://github.com/vintasoftware/aurorae/tree/main/aurorae/providers/spreadsheet) for an example.\n\nThe historic and architecture details can be found on the [project\'s ADRs](https://github.com/vintasoftware/aurorae/blob/main/docs/adr/README.md).\n\n## Requirements\n\n- Python (>3)\n- openpyxl (3.0.7)\n- pydantic (>1.8.2)\n\n## Installation\n\n```\npip install aurorae\n```\n\n## Usage\nTo run aurorae with test data:\n```bash\ngenerate_cnab_sample\n```\n\nTo run aurorae with your own data use:\n\n```bash\ngenerate_cnab_sample ~/source_spreadsheet.xlsx\n```\n\n## Documentation\nhttps://aurorae.readthedocs.io\n\n## Security\nWe take aurorae\'s security and our users\' trust seriously, therefore we do not save any information (from payments or not) sent by users. If you believe you have found a security issue, please responsibly disclose by contacting: [flavio@vinta.com.br](flavio@vinta.com.br)\n\n## Releases\n\nSee [CHANGELOG.md](https://github.com/vintasoftware/aurorae/blob/main/CHANGELOG.md).\n\n## Credits\n\nThis project is maintained by [open-source contributors](https://github.com/vintasoftware/aurorae/blob/main/AUTHORS.rst) and [Vinta Software](https://www.vintasoftware.com/).\n\n## Commercial Support\n\n[Vinta Software](https://www.vintasoftware.com/) is always looking for exciting work, so if you need any commercial support, feel free to get in touch: contact@vinta.com.br\n',
    'author': 'Mariane Pastor (Vinta Software)',
    'author_email': 'mariane.pastor@vinta.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
