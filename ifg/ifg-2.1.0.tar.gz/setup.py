# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ifg']

package_data = \
{'': ['*']}

install_requires = \
['fdint>=2.0,<3.0']

extras_require = \
{':python_version ~= "2.7"': ['numpy>=1.16.6,<2.0.0', 'scipy>=1.2,<2.0'],
 ':python_version ~= "3.5.2"': ['numpy>=1.18.5,<2.0.0', 'scipy>=1.4,<2.0'],
 ':python_version ~= "3.6"': ['numpy>=1.19.5,<2.0.0', 'scipy>=1.5,<2.0'],
 ':python_version ~= "3.7"': ['numpy>=1.20.3,<2.0.0', 'scipy>=1.6,<2.0'],
 ':python_version ~= "3.8"': ['numpy>=1.20.3,<2.0.0', 'scipy>=1.6,<2.0'],
 ':python_version ~= "3.9"': ['numpy>=1.20.3,<2.0.0', 'scipy>=1.6,<2.0']}

setup_kwargs = {
    'name': 'ifg',
    'version': '2.1.0',
    'description': 'Calculator of Ideal Fermi gas properties',
    'long_description': '# Numerical ideal Fermi gas\n\n[![Documentation Status](https://readthedocs.org/projects/ifg-py/badge/?version=latest)](https://ifg-py.readthedocs.io/en/latest/?badge=latest)\n[![tests](https://github.com/alekseik1/ifg-py/workflows/tests/badge.svg?branch=master)](https://github.com/alekseik1/ifg-py/actions?query=workflow%3A%22tests%22)\n[![examples](https://github.com/alekseik1/ifg-py/workflows/examples/badge.svg?branch=master)](https://github.com/alekseik1/ifg-py/actions?query=workflow%3A%22examples%22)\n[![CodeQL](https://github.com/alekseik1/ifg-py/workflows/CodeQL/badge.svg?branch=master)](https://github.com/alekseik1/ifg-py/actions?query=workflow%3A%22CodeQL%22)\n[![build and deploy](https://github.com/alekseik1/ifg-py/workflows/build%20and%20deploy/badge.svg?branch=master)](https://github.com/alekseik1/ifg-py/actions)\n[![codecov](https://codecov.io/gh/alekseik1/ifg-py/branch/master/graph/badge.svg?token=45T6I5O81G)](https://codecov.io/gh/alekseik1/ifg-py)\n\n## Getting started\n```bash\npip install ifg\n```\n\n## Functionality\nThe module can calculate some properties (like pressure, entropy) for ideal Fermi gas model.\n\nSee [API reference](https://ifg-py.readthedocs.io/en/latest/) for more information\n\n\n## Examples\nSee `examples/` folder for plots and code examples.\n\n## Acknowledgements\n- [Library for Fermi integrals](https://pypi.org/project/fdint/)\n\n\n## Reporting bugs\nUse *Issues* to report any errors or bugs.\n',
    'author': 'Aleksei Kozharin',
    'author_email': '1alekseik1@gmail.com',
    'maintainer': 'Aleksei Kozharin',
    'maintainer_email': '1alekseik1@gmail.com',
    'url': 'https://github.com/alekseik1/ifg-py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
}


setup(**setup_kwargs)
