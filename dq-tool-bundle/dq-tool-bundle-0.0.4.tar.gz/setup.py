# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dqtoolbundle', 'dqtoolbundle.test']

package_data = \
{'': ['*'], 'dqtoolbundle': ['_config/*']}

install_requires = \
['dq-tool>=0.0.4,<0.1.0', 'ipython==7.12.0', 'pyfony-bundles>=0.4.0,<0.5.0']

entry_points = \
{'pyfony.bundle': ['create = dqtoolbundle.DQToolBundle:DQToolBundle']}

setup_kwargs = {
    'name': 'dq-tool-bundle',
    'version': '0.0.4',
    'description': 'DQ Tool for the Daipe AI Platform',
    'long_description': '# DQ Tool bundle\n',
    'author': 'DataSentics',
    'author_email': 'info@datasentics.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/daipe-ai/dq-tool-bundle',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
