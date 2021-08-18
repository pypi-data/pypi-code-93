# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['lonelyconnect']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'MarkupSafe>=2.0.1,<3.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'aiofiles>=0.7.0,<0.8.0',
 'fastapi>=0.68.0,<0.69.0',
 'python-multipart>=0.0.5,<0.0.6',
 'uvicorn>=0.15.0,<0.16.0']

entry_points = \
{'console_scripts': ['lonelyconnect = lonelyconnect:entrypoint']}

setup_kwargs = {
    'name': 'lonelyconnect',
    'version': '0.1.0',
    'description': 'Make your own OnlyConnect-style quizzes at home',
    'long_description': '# LonelyConnect\n\n[![pytest](https://github.com/L3viathan/lonelyconnect/actions/workflows/pytest.yml/badge.svg)](https://github.com/L3viathan/lonelyconnect/actions/workflows/pytest.yml)\n\nThis is a fan-made implementation of the BBC quiz show OnlyConnect. It\nallows you to write your own riddles and host your own show at home. For partly\ntechnical and partly gameplay reasons, round 3 (the connecting wall) is not\nimplemented.\n\nIn case this isn\'t clear enough yet: This repository is not associated with the\nshow at all, and no assets (images, audio, ...) of the original show are used.\n\n\n# Usage\n\nStart the uvicorn app, e.g. via\n\n    uvicorn lonelyconnect:app\n\nIt will print out an admin code. Alternatively, you can set the environment\nvariable `lonelyconnect_admin_code`.\n\nLonelyConnect requires 4 "devices" (browser tabs):\n\n- One connected to the admin interface (for the quiz master)\n- Two for the teams (one each), showing the buzzers\n- One for the "stage"; this could be projected on a large screen, it shows\n  public information and requires no authentication.\n\nTo connect to anything but the stage, just go to the root path (`/`), by\ndefault on port 8000. This will present you with a large text input, in which\nyou can enter the authentication code. The admin code is obtained as described\nabove, the codes for the two buzzers can be retrieved via the admin interface.\n\nThe stage is available at `/ui/stage`.\n\nOnce everyone is connected, you can test the buzzers by setting the buzz mode\nmanually via the admin interface. During the course of a normal game, the buzz\nstate (who is allowed to buzz/who has buzzed) will be automatically set through\nthe game logic.\n\nTo start a game, the admin can load a game file.\n\nAfterwards, the admin interface is usable through numeric keyboard shortcuts (as displayed on the dashboard).\n',
    'author': 'L3viathan',
    'author_email': 'git@l3vi.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/L3viathan/lonelyconnect',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
