# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['e4l']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0', 'impacket>=0.9.23,<0.10.0', 'ldap3>=2.9.1,<3.0.0']

entry_points = \
{'console_scripts': ['e4l = e4l.__main__:main']}

setup_kwargs = {
    'name': 'e4l',
    'version': '0.1.2',
    'description': 'enum4linux-ng but pip installable',
    'long_description': '# e4l\n\n## Motivation\n\nThis is [enum4linux-ng]() but you can install it via pip, because this h4x0rish installations suck.\n\n## Installation\n\n```\npip install e4l\n```\n\n## License\n\nThis project is licensed under the GPL-3 license.\n',
    'author': '4thel00z',
    'author_email': '4thel00z@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/4thel00z/e4l',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
