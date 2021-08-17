# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crak']

package_data = \
{'': ['*']}

install_requires = \
['argparse>=1.4.0,<2.0.0', 'pandas>=1.3.2,<2.0.0', 'passlib>=1.7.4,<2.0.0']

entry_points = \
{'console_scripts': ['crak = crak.cli:main']}

setup_kwargs = {
    'name': 'crak',
    'version': '0.0.2',
    'description': 'Bruteforce password cracker',
    'long_description': '# crak\n\nA password file dictionary based password cracker\n\n## requirements\n\n1. linux shadow password file containing passwords to attack\n2. file containing word dictionary.\n\n## usage\n\n### installation\n\n`pip install crak`\n\n### help\n\n```\ncrak -h\nusage: crak [-h] [--version] [-d WORDDICT] [-u USERNAME] shadowfile\n\nPerform a dictionary crack on a list of encrypted passwords using a wordlist\n\npositional arguments:\n  shadowfile            Shadow password file containing crypted passwords\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --version             prints version information\n  -d WORDDICT, --worddict WORDDICT\n                        Word dictionary files to use in attack\n  -u USERNAME, --username USERNAME\n                        specific username - if not defined then all users in\n                        shadow file will be attempted\n```\n\n### list users\n\nwill list all valid users in the shadow file and is useful to see what username to target specifically\n\n```\ncrak shadow \n\n-=( crak v 0.0.1 )=-\n\nlist of usernames in shadow file\n                                                        password\nusername                                                        \nroot           $6$QlJt0cnr$hmgN/fzUrHFFI1SaGXVNzE060TPuwsZdzP...\nbackup         $6$Tye3KuC5$rVIT3u5M9IhZZI.jRanteGT3o7DbkLFWb/...\nallison        $6$sPsSvR2J$wk59pi4or6QR5IobArTZpn4k7i2jZQ07pY...\npaul           $6$YGG4oFLp$avrVGY6.S59aApmCY/60A7AWfGDBh/zI7L...\ndr_balustrade  $6$3kgge6ym$OcIOZS8bJy41YsLYXToOW2Ag3imG1KEXkP...\n```\n\n### dictionary attack all users\n\nwill run a dictionary attack against all the valid users in the shadow file\n\n```\ncrak shadow -d dicttest.txt\n\n-=( crak.py v 0.0.1 )=-\n\nstarting to crack passwords for all users\nNo password found: root\nNo password found: backup\nNo password found: allison\nNo password found: paul\n*** FOUND PASSWORD ***\nUsername: dr_balustrade\nPassword: pinky\n**********************\n```\n\n### Specify user to perform brute force attack on\n\nWill target a specific user\n\n```\ncrak shadow -d dicttest.txt -u dr_balustrade\n\n-=( crak v 0.0.1 )=-\n\nstarting to crack password for user: dr_balustrade\n*** FOUND PASSWORD ***\nUsername: dr_balustrade\nPassword: pinky\n**********************\n```\n\n### Display version\n\ndisplays the current version\n\n```\ncrak --version\ncrak v0.0.1\n```\n',
    'author': 'Stephen Eaton',
    'author_email': 'seaton@strobotics.com.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/madeinoz67/crak',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1',
}


setup(**setup_kwargs)
