# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simsam']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.4,<2.0.0']

setup_kwargs = {
    'name': 'simsam',
    'version': '0.1.3',
    'description': 'Simplex sampling algorithm',
    'long_description': '# `Simsam`: Simplex Sampling Methods\n\nThis small package implements methods for sampling from a unit simplex,\na problem that often crops up in a data analysis context.\n\n## Usage\n\nThere is only a single sampling strategy that results in uniform samples\nfrom the unit simplex:\n\n```python\nfrom simsam import kraemer_sampling\n\n# Sample 1,000 points from the 10-dimensional unit simplex.\ndim = 10\nN = 1000\nsamples = kraemer_sampling(dim, N)\n```\n\nFor comparison purposes, there is also a naive sampling procedure, which\ndoes *not* result in uniform samples.\n\n```python\nfrom simsam import naive_sampling\n\n# Sample 1,000 points from the 10-dimensional unit simplex. Notice that\n# the samples will be biased.\ndim = 10\nN = 1000\nsamples = naive_sampling(dim, N)\n```\n',
    'author': 'Bastian Rieck',
    'author_email': 'bastian@rieck.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Pseudomanifold/Simsam',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
