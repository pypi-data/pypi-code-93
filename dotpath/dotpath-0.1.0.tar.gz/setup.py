# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dotpath']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dotpath',
    'version': '0.1.0',
    'description': 'A module to access Python props using dotpath.',
    'long_description': "# dotpath\nA simple module to access Python props using dotpath.\n\n## Example\n```python\nfrom dotpath import dotpath\n\n# A object\npets_dic = {\n    'pets': {\n        'dog': {\n            'name': 'Billy',\n            'age': 5,\n            'friends': ['Joe', 'Jack'],\n        },\n        'cat': {\n            'name': 'Joe',\n            'age': 6,\n            'friends': ['Billy', 'Pop'],\n        },\n    },\n}\n\ndog_name = getpath(pets_dic, 'pets.dog.name') # Returns Billy\ncat_name = getpath(pets_dic, 'pets.cat.name') # Returns Joe\n```",
    'author': 'Silas Vasconcelos',
    'author_email': 'silasvasconcelos@hotmail.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/silasvasconcelos/dotpath',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
