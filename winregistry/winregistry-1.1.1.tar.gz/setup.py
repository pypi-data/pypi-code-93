# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['robot', 'winregistry', 'winregistry.robot']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'winregistry',
    'version': '1.1.1',
    'description': 'Library aimed at working with Windows registry',
    'long_description': '# winregistry\n\nMinimalist Python library aimed at working with Windows Registry.\n\n## Installation\n\n```bash\npip install winregistry\n```\n\n## Usage\n\n```py\nfrom winregistry import WinRegistry\n\nTEST_REG_PATH = r"HKLM\\SOFTWARE\\_REMOVE_ME_"\n\n\nif __name__ == "__main__":\n    with WinRegistry() as client:\n        client.create_key(TEST_REG_PATH)\n        client.write_entry(TEST_REG_PATH, "remove_me", "test")\n        test_entry = client.read_entry(TEST_REG_PATH, "remove_me")\n        assert test_entry.value == "test"\n        client.delete_entry(TEST_REG_PATH, "remove_me")\n```\n\nUsage with ``Robot Testing Framework`` Library\n----------------------------------------------\n\n```\n*** Settings ***\nLibrary    winregistry.robot\n\n*** Test Cases ***\nValid Login\n        ${path} =    Set Variable    HKLM\\\\SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run\n        Write Registry Entry    ${path}             Notepad   notepad.exe\n        ${autorun} =            Read Registry Key   ${path}\n        Delete Registry Entry   ${path}             Notepad\n```\n',
    'author': 'Aleksandr Shpak',
    'author_email': 'shpaker@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/shpaker/winregistry',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
