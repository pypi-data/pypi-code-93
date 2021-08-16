# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kit', 'kit.pl', 'kit.torch', 'kit.torch.transforms']

package_data = \
{'': ['*']}

extras_require = \
{'all': ['pytorch-lightning>=1.4.2,<2.0.0',
         'hydra-core>=1.1.0,<2.0.0',
         'pandas>=1.3.1,<2.0.0',
         'wandb>=0.12.0,<0.13.0'],
 'hydra': ['hydra-core>=1.1.0,<2.0.0'],
 'pl': ['pytorch-lightning>=1.4.2,<2.0.0', 'tqdm>=4.62.0,<5.0.0'],
 'torch': ['torch>=1.8,<2.0', 'numpy>=1.20.3,<2.0.0'],
 'wandb': ['pandas>=1.3.1,<2.0.0', 'wandb>=0.12.0,<0.13.0']}

setup_kwargs = {
    'name': 'palkit',
    'version': '0.3.11',
    'description': 'Useful functions.',
    'long_description': '# PAL kit\n\nThis is a collection of useful functions for code that we write in our group.\n\n## Install\n\nRun\n```\npip install palkit\n```\n\nor install directly from GitHub:\n```\npip install git+https://github.com/predictive-analytics-lab/palkit.git@main\n```\n',
    'author': 'PAL',
    'author_email': 'info@predictive-analytics-lab.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/predictive-analytics-lab/palkit',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
