# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['python_dataset', 'python_dataset.property', 'python_dataset.wave']

package_data = \
{'': ['*']}

install_requires = \
['jupyterlab>=3.1.4,<4.0.0',
 'librosa>=0.8.1,<0.9.0',
 'opencv-python>=4.5.2,<5.0.0',
 'pandas>=1.2.4,<2.0.0',
 'pysptk>=0.1.18,<0.2.0',
 'pyworld>=0.2.12,<0.3.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'python-dataset',
    'version': '0.0.1',
    'description': '',
    'long_description': None,
    'author': 'kjun1',
    'author_email': 'p.k.maejima1211@icloud.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.11,<4.0.0',
}


setup(**setup_kwargs)
