# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cvcreator']

package_data = \
{'': ['*'], 'cvcreator': ['icons/*', 'templates/*']}

install_requires = \
['Jinja2>=2.11.3,<3.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'click-help-colors>=0.9,<0.10',
 'click>=8.0.1,<9.0.0',
 'pydantic>=1.8.1,<2.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['cv = cvcreator.__main__:cv',
                     'cvcreate = cvcreator.__main__:create']}

setup_kwargs = {
    'name': 'cvcreator',
    'version': '1.0.2',
    'description': 'An automated tool for creating CVs on the fly.',
    'long_description': None,
    'author': 'Jonathan Feinberg',
    'author_email': 'jonathf@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
