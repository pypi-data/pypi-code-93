# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wallger']

package_data = \
{'': ['*']}

install_requires = \
['colorama>=0.4.4,<0.5.0', 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['wallger = wallger:main']}

setup_kwargs = {
    'name': 'wallger',
    'version': '1.2.0',
    'description': 'Wallpaper changer for Linux, get images from Wallhaven, Unsplash and others!',
    'long_description': '# Wallger: The Wallpaper Changer\n\n![CodeQL](https://github.com/UltiRequiem/wallger/workflows/CodeQL/badge.svg)\n![Pylint](https://github.com/UltiRequiem/wallger/workflows/Pylint/badge.svg)\n[![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)\n[![PyPi Version](https://img.shields.io/pypi/v/wallger)](https://pypi.org/project/wallger)\n![Repo Size](https://img.shields.io/github/repo-size/ultirequiem/wallger?style=flat-square&label=Repo)\n[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)\n![Lines of Code](https://img.shields.io/tokei/lines/github.com/UltiRequiem/wallger?color=blue&label=Total%20Lines)\n\nhttps://user-images.githubusercontent.com/71897736/129631224-d4f00320-265c-4514-9086-a01b26cfdfd2.mp4\n\n## Install\n\nYou can install [Wallger](https://pypi.org/project/wallger) from PyPI like\nany other package:\n\n```bash\npip install wallger\n```\n\nTo get the last version:\n\n```bash\npip install git+https:/github.com/UltiRequiem/wallger\n```\n\nIf you use Linux, you may need to install this with sudo to\nbe able to access the command throughout your system.\n\n## Example Config\n\nThis configuration goes in `~/.config/wallger/config.json`:\n\n```json\n{\n  "resolution": [1600, 900],\n  "provider": "wallhaven",\n  "path": "/home/zero/disk/sabare/wallger",\n  "topic": "anime",\n  "tool": "feh",\n  "nsfw": false\n}\n```\n\n- Resolution: The resolution of you monitor\n- Provider: It can be Wallhaven or Unsplash\n- Path: Where to save the images\n- Topic: The topic (Eg. "Math", "Code Geass", "Mirai Nikki")\n- Tool: The tool to change the Wallpaper. Options = ["feh","gnome","mate","kde"]\n- NSFW: No safe for work\n\nThere are not default values.\n\n### License\n\nWallger is licensed under the [MIT License](./LICENSE).\n',
    'author': 'Eliaz Bobadilla',
    'author_email': 'eliaz.bobadilladev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/UltiRequiem/wallger',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
