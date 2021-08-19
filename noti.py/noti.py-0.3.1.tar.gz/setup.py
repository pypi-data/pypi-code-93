# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['noti_py', 'noti_py.config']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0', 'click>=8.0.1,<9.0.0', 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['notipy = noti_py.noti:main']}

setup_kwargs = {
    'name': 'noti.py',
    'version': '0.3.1',
    'description': 'Python-based notification script to post a message to a materix server via the Matrix client/server API',
    'long_description': '<img src="https://raw.githubusercontent.com/kellya/notipy/master/images/notipy.svg" width="200">\n\n# noti.py\nSimple Python-based notification script to post to a matrix server via the Matrix client/server API\n\nThis is not an interactive chat bot.  The use case is to have scripts send alerts to a single alert channel.\n\n# How to install\n## Via PyPi\nAs of version 0.0.6, noti.py has been published to PyPi, so installing (should\nbe) as easy as\n`pip install noti_py`\n\nThis will also create a `notipy` "entrypoint" to use as the binary to run.\n\n## Via git\n1.  clone the repo\n2.  install the requirements `pip install -r requirements.txt`\n3.  `cp example-config.yaml <config_dir>config.yaml`\n4.  Edit the config.yaml to your local needs\n5.  Then just use `./noti.py --help` to figure out what options you can specify\n\n<config_dir> referenced in step 3 above will be checked in the following order\nor preference\n1. . (current directory)\n2. ~/.config/noti_py\n3. /etc/noti_py\n\nIf you want it in another location completely, specify the `--config` option to\noverride.\n\n# How do I use this thing?\nstart with `noti.py --help` to see a list of the commands you can use.  Generally you are going to need to do the following things:\n\n1. Create a user on your server for this script to connect as\n2. Connect to a room by either:\n    1. Creating a new room `noti.py create`\n    or\n    2. Joining a room `noti.py join` if you\'ve already invited the user from step 1 with a different user\n3.  Edit the config.yaml to put in your access token and all your homeserver configuration.  If you don\'t know your token, you can get it by running `./noti.py token`\n\nAt this point you should be able to send a message with: `./noti.py send "message to send"` or if you are so inclined, you can pipe stdin to the script with `echo "message to send"|./noti.py send`\n# Inspiration\nI tried to use [mnotify](https://matrix.org/docs/projects/client/mnotify) which is written in go.  When I ran `make`, it gave a segfault upon running `mnotify`.  Rather than try to learn go, I decided to just try to do the same thing in python.\n\n# Contribute\nFeel free to fork, make updates and submit a pull request for new things or to fix some horrible python atrocity I have commited ;)\n\n# Chat\nYou can join me on matrix at https://matrix.to/#/#noti.py:arachnitech.com\n\n# Notes\nI started using matrix 3 days ago.  There are a lot of things about its operation that I haven\'t figure out yet.  This will hopefully progress as I figure things out, but beware that this approach may not be the best one.\n',
    'author': 'Alex Kelly',
    'author_email': 'kellya@arachnitech.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kellya/notipy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
