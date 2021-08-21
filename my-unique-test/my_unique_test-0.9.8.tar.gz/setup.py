# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['my_unique_test']

package_data = \
{'': ['*']}

install_requires = \
['bump2version>=1.0.1,<2.0.0']

setup_kwargs = {
    'name': 'my-unique-test',
    'version': '0.9.8',
    'description': '',
    'long_description': '# commit_with_tag_version',
    'author': 'Leandro G. Almeida',
    'author_email': 'leandro.g.almeida@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/lalmei/commit_with_tag_version',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<3.10',
}


setup(**setup_kwargs)
