# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['perm_banana', 'perm_banana.CheckStrategy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'perm-banana',
    'version': '0.2.0',
    'description': 'A Bitwise Permission Handler',
    'long_description': '\n# Perm-Banana\n\n#### A package to enable easy permission creation inside Python.\n\n#### How to use it?\n\n```python\nfrom perm-banana import Permission, Check, banana\n\n@banana\nclass MyPermission(Permission)\n    can_read_messages = Check(Permission(0b1))\n    can_write_messages = Check(Permission(0b10))\n    basic_user = can_read_message | can_write_messages\n\nuser = MyPermission(0b11)\nif user.basic_user:\n    print("permission granted")\nelse:\n    print("permission denied")\n```\n',
    'author': 'TheJoeSmo',
    'author_email': 'joesmo.joesmo12@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TheJoeSmo/perm-banana',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
