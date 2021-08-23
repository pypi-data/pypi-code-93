# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pysmo', 'pysmo.core', 'pysmo.core.sac', 'pysmo.tools', 'pysmo.tools.noise']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'matplotlib>=3.3.3,<4.0.0',
 'numpy>=1.19.4,<2.0.0',
 'pyproj>=3.0.0,<4.0.0',
 'requests>=2.25.1,<3.0.0',
 'scipy>=1.5.4,<2.0.0']

setup_kwargs = {
    'name': 'pysmo',
    'version': '0.8.0',
    'description': 'Python module to read/write/manipulate SAC (Seismic Analysis Code) files',
    'long_description': '[![Build Status](https://travis-ci.com/pysmo/pysmo.svg?branch=master)](https://travis-ci.com/pysmo/pysmo)\n[![Documentation Status](https://readthedocs.org/projects/pysmo/badge/?version=latest)](https://pysmo.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/pysmo/pysmo/branch/master/graph/badge.svg?token=ZsHTBN4rxF)](https://codecov.io/gh/pysmo/pysmo)\n\nPysmo\n=====\n\nPython package to read/write/manipulate SAC (Seismic Analysis Code) files.\n\nDocumentation\n-------------\n\nThe complete pysmo documentation is available at https://pysmo.readthedocs.io/\n\nContributors\n------------\n\n- Helio Tejedor',
    'author': 'Simon M. Lloyd',
    'author_email': 'simon@slloyd.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
