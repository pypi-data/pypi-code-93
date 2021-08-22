# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chillboss']

package_data = \
{'': ['*']}

install_requires = \
['PyAutogui>=0.9.50,<0.10.0',
 'click>=7.1.2,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'emoji>=1.2.0,<2.0.0',
 'importlib-metadata>=4.0.1,<5.0.0',
 'pyfiglet>=0.8.post1,<0.9']

entry_points = \
{'console_scripts': ['chillboss = chillboss.__main__:chill']}

setup_kwargs = {
    'name': 'chillboss',
    'version': '0.4.0',
    'description': "Let's chill, Pointer moves forever.",
    'long_description': '# ChillBoss\n\n[![Downloads](https://static.pepy.tech/personalized-badge/chillboss?period=total&units=international_system&left_color=blue&right_color=green&left_text=Total%20Downloads)](https://pepy.tech/project/chillboss)\n[![Monthly_Downloads](https://static.pepy.tech/personalized-badge/chillboss?period=month&units=international_system&left_color=blue&right_color=green&left_text=Downloads/Month)](https://pepy.tech/project/chillboss)\n[![Weekly_Downloads](https://static.pepy.tech/personalized-badge/chillboss?period=week&units=international_system&left_color=blue&right_color=green&left_text=Downloads/Week)](https://pepy.tech/project/chillboss)\n[![Hygiene](https://github.com/NaveenKumarReddy8/ChillBoss/actions/workflows/main.yml/badge.svg)](https://github.com/NaveenKumarReddy8/ChillBoss/actions/workflows/main.yml)\n[![chillboss](https://snyk.io/advisor/python/chillboss/badge.svg)](https://snyk.io/advisor/python/chillboss)\n[![PyPI version fury.io](https://badge.fury.io/py/chillboss.svg)](https://pypi.python.org/pypi/chillboss/)\n\nVersion: 0.4.0\n\nChillBoss keeps your mouse moving to keep your status alive 😎.\n\nHomepage: https://naveenkumarreddy8.github.io/ChillBoss/\n\nInstallation:\n\nChillBoss is published on PyPI: https://pypi.org/project/chillboss/ \n\n```shell\npip install chillboss\n```\n\n---\n\n**NOTE**\n\nOn Linux you may need to install python3-tk python3-dev\n\n```\nsudo apt-get install python3-tk python3-dev\n```\n\n---\n\n\n![ChillBoss Installation](https://media.giphy.com/media/aDoezJuCfRnEf4KErq/source.gif)\n\nUsage:\n\n```shell\nchillboss [options]\n```\n\nCommand line argument accepted:\n\n* -m, --movement: `random` and `square` movements are accepted. Default set to `random`.\n* -l, --length: Accepted for `square` type of movement. Default set to `None`.\n* -s, --sleeptime: Time to be taken till next movement. Default set to 30 seconds.\n* -mt, --motiontime: Time consumption of pointer to move from present coordinates to the next coordinates. Default set to 0\n  seconds.\n* -v, --verbose: Flag argument when given as input, sets the log level to Debug, else Warning.\n\n![ChillBoss Usage](https://media.giphy.com/media/TrlvEhASiYMqNZ7Gy9/source.gif)\n\n\nMade with love ❤️',
    'author': 'NaveenKumarReddy8',
    'author_email': 'mr.naveen8@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://naveenkumarreddy8.github.io/ChillBoss/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
