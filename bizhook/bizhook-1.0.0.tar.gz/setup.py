# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bizhook']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'bizhook',
    'version': '1.0.0',
    'description': 'Communicate with the Bizhawk emulator via a Lua socket',
    'long_description': "# Bizhawk Hook\n\nInteract with [Bizhawk](http://tasvideos.org/Bizhawk.html) via a socket server hosted in the Lua Console.\n\n## How to use\n\n### Bizhawk Lua\n\n#### Exporting\n\nExport all the necessary Lua components using the provided function.\n```py\nfrom bizhook import export_lua_components\n\nexport_lua_components('/home/williamson/.bizhook')\n```\nYou can either provide a path or leave it empty to have it open up a file dialogue asking for directory.\n\n#### Opening socket\n\nIn Bizhawk, go to `Tools` > `Lua Console`. Select `Open script` and open `hook.lua` from the exported components.\n\n##### Is it working?\n\nIf it starts successfully, you should see a text in the top-left of the emulator saying the socket is being opened. Should that not appear, try restarting the emulator until it does. This seems to be an issue with Bizhawk.\n\n**Note**: Do not try to communicate with the socket *before* the text has disappeared, as it isn't actually opened yet. The message is there to make it clear that the script is running successfully.\n\n### Python\n\nYou can read from and write to memory by using a `Memory` object.\n```py\nfrom bizhook import Memory\n\ncombined_wram = Memory('Combined WRAM')\n```\n\nTo see the available methods, do `help(Memory)`.\n\n#### Memory domain\nYou can use the default memory domain by providing an empty string. However, I would advice against it and that you always do specify with which domain you want to interact. It may be that it works for you solely because, per chance, the default one happens to be the correct one.",
    'author': 'Maximillian Strand',
    'author_email': 'maximillian.strand@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/thedisruptproject/bizhook',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
