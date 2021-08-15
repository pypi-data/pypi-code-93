# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['panthera']

package_data = \
{'': ['*']}

install_requires = \
['ase>=3.22.0,<4.0.0',
 'bmatrix>=1.0.1,<2.0.0',
 'lxml>=4.6.3,<5.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'numpy>=1.21.1,<2.0.0',
 'numpydoc>=1.1.0,<2.0.0',
 'pandas>=1.3.1,<2.0.0',
 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'panthera',
    'version': '0.5.2',
    'description': 'Package for calculating thermochemistry with anharmonic corrections',
    'long_description': '\n# panthera - program for anharmonic thermochemistry\n\n## Installation\n\nThe recommended installation method is with [pip]. The latest version\ncan be installed directly from [bitbucket repository]:\n\n```bash\npip install https://github.com/lmmentel/panthera.git\n```\nor cloned first\n```bash\ngit clone https://github.com/lmmentel/panthera.git\n```\nand installed via\n```bash\npip install -U [--user] ./panthera\n```\n\n[pip]: https://pip.pypa.io/en/stable/\n\n## Documentation\n\nThe documentatioan can be at [panthera.rtfd.io](http://panthera.rtfd.io).\n\n## Citing\n\nIf you use *panthera* in a scientific publication, please cite the software as\n\n|    L. M. Mentel, *panthera* - Package for Anharmonic Thermochemistry, 2016. Available at: [https://github.com/lmmentel/panthera](https://github.com/lmmentel/panthera)\n\n\n## Funding\n\nThis project is supported by the RCN (The Research Council of Norway) project\nnumber 239193.\n\n',
    'author': 'Lukasz Mentel',
    'author_email': 'lmmentel@gmail.com',
    'maintainer': 'Lukasz Mentel',
    'maintainer_email': 'lmmentel@gmail.com',
    'url': 'https://github.com/lmmentel/panthera',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
