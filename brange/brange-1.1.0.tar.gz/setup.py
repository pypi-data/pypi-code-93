# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brange']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'brange',
    'version': '1.1.0',
    'description': 'A range which automatically deals with either direction.',
    'long_description': '# Better Range\n\nA range which automatically deals with either direction.\n\n\n### Installation\n```\npip install brange\n```\n\n### Usage\n\nStart is always inclusive and end is always exclusive. Step must be a positive integer, as it always steps toward the end. A negative value will result in an empty range.\n\n#### Regular\n\n```py\nfrom brange import brange\n\n# This will create a list between 10 (inclusive) and -40 (exclusive)\n# [10, 11, 12, ... -37, -38, -39]\n[i for i in brange(10, -40)]\n```\n\n#### N-dimensional\n\n```py\nfrom brange import nbrange\n\ndimensions = [\n    (1, 10, 2), # X\n    (3, -2, 1), # Y\n    (-2, 5, 1), # Z\n]\n\n[xyz for xyz in nbrange(*dimensions)]\n\n# This will result in a list as below:\n# [\n#     (1, 3, -2),\n#     (1, 3, -1),\n#     ...\n#     (9, -1, 2),\n#     (9, -1, 3),\n#     (9, -1, 4),\n# ]\n```',
    'author': 'Maximillian Strand',
    'author_email': 'maximillian.strand@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
