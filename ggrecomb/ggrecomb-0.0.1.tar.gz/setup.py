# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ggrecomb', 'ggrecomb.tools']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.79,<2.0', 'scipy>=1.6.3,<2.0.0']

setup_kwargs = {
    'name': 'ggrecomb',
    'version': '0.0.1',
    'description': 'Design recombinant protein libraries for Golden Gate Assembly.',
    'long_description': None,
    'author': 'Bennett Bremer',
    'author_email': 'bennettjamesbremer@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9.1,<3.10.0',
}


setup(**setup_kwargs)
