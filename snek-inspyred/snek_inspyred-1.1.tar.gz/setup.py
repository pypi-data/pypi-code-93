# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['snek_inspyred',
 'snek_inspyred.conf',
 'snek_inspyred.game',
 'snek_inspyred.game.audio',
 'snek_inspyred.game.audio.assets',
 'snek_inspyred.game.audio.conf',
 'snek_inspyred.game.field',
 'snek_inspyred.game.models',
 'snek_inspyred.helpers']

package_data = \
{'': ['*'], 'snek_inspyred.game': ['audio/conf/conf_files/*']}

install_requires = \
['pygame>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['snek = snek_inspyred.main:snek.main']}

setup_kwargs = {
    'name': 'snek-inspyred',
    'version': '1.1',
    'description': 'The classic snake game, just in Python.',
    'long_description': None,
    'author': 'Taylor B.',
    'author_email': '43686206+tayjaybabee@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
