# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tuhlbox']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'dstoolbox>=0.10.1,<0.11.0',
 'gensim>=3.8.3,<4.0.0',
 'simpletransformers>=0.51.1,<0.52.0',
 'sklearn>=0.0,<0.1',
 'skorch>=0.10.0,<0.11.0',
 'stanza>=1.1.1,<2.0.0',
 'torch>=1.7.0,<2.0.0',
 'treegrams>=0.1.0,<0.2.0']

entry_points = \
{'console_scripts': ['parse_dependency = tuhlbox.cli:parse_dependency',
                     'reddit_to_common = tuhlbox.cli:reddit_to_common',
                     'translate = tuhlbox.cli:translate']}

setup_kwargs = {
    'name': 'tuhlbox',
    'version': '0.4.8',
    'description': 'Personal toolbox of language processing models.',
    'long_description': None,
    'author': 'Benjamin Murauer',
    'author_email': 'b.murauer@posteo.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.uibk.ac.at/csak8736/tuhlbox',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
