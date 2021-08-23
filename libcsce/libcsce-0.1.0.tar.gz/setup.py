# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libcsce', 'libcsce.bin']

package_data = \
{'': ['*']}

install_requires = \
['pefile>=2019.4.18']

entry_points = \
{'console_scripts': ['csce = libcsce.bin.csce:main',
                     'list-cs-settings = libcsce.bin.list_cs_settings:main']}

setup_kwargs = {
    'name': 'libcsce',
    'version': '0.1.0',
    'description': 'Cobalt Strike configuration extractor and parser library and scripts.',
    'long_description': "#################################################\nCobalt Strike Configuration Extractor and Parser\n#################################################\n\nOverview\n=========\n\nPure Python library and set of scripts to extract and parse configurations (configs) from `Cobalt Strike Beacons <https://www.cobaltstrike.com/help-beacon>`_.\nThe library, ``libcsce``, contains classes for building tools to work with Beacon configs.\nThere are also two CLI scripts included that use the library to parse Beacon config data:\n\n1. ``csce``: Parses all known Beacon config settings to JSON,\n   mimicing the `Malleable C2 profile <https://cobaltstrike.com/help-malleable-c2>`_ structure.\n2. ``list-cs-settings``: Attempts to find by brute-force the associated Cobalt Strike version, and all settings/their types, of a Beacon config.\n   This script is useful for conducting research on Beacon samples.\n\nInstallation\n=============\n\nInstall from Pypi (preferred method)\n-------------------------------------\n\n.. code-block:: bash\n\n   > pip install libcsce\n\nInstall from GitHub with Pip\n-----------------------------\n\n.. code-block:: bash\n\n    > pip install git+ssh://git@github.com/strozfriedberg/cobaltstrike-config-extractor.git#egg=libcsce\n\nInstall from Cloned Repo\n-------------------------\n\n.. code-block:: bash\n\n    > git clone ssh://git@github.com/strozfriedberg/cobaltstrike-config-extractor.git\n    > cd libcsce\n    > pip install .\n\nDependencies\n=============\n\nThe only external non-development dependency is `pefile <https://github.com/erocarrera/pefile>`_,\nwhich is required to decrypt Beacon configs from the ``.data`` section of PE files.\nRequires **Python 3.6+**.\n\nDevelopment dependencies include those specified in ``pyproject.toml`` as well as:\n\n- `Poetry <https://python-poetry.org/docs/>`_\n- `Make <https://www.gnu.org/software/make/>`_\n\nGetting Started\n================\n\ncsce\n-----\n\nBoth of the CLI scripts support extracting Beacon configs from PE files (DLLs/EXEs) and memory dumps where a Beacon was running.\nTo parse a Beacon PE file to JSON, use ``csce``:\n\n.. code-block:: bash\n\n    > csce --pretty <path/to/file.{exe,dll,bin,dmp}>\n\nBy default, the script will try to parse the Beacon as version ``3`` and, if that fails, try version ``4``.\nYou can specify a version manually via the ``-v`` flag to save cycles if you know the Beacon is version ``4``\n(using ``-v 3`` doesn't technically save cycles because the script tries that version first by default).\n\nlist-cs-settings\n-----------------\n\nTo discover new settings and while conducting research, sometimes it's useful to extract possible all settings and their types from a Beacon sample.\nUse ``list-cs-settings`` to detect by brute-force the Cobalt Strike version and all settings/types:\n\n.. code-block:: bash\n\n    > list-cs-settings <path/to/file.{exe,dll,bin,dmp}>\n\nThis script produces JSON where the top-level key is the Cobalt Strike version number,\nwhich points to a mapping from setting number to information about that setting, including:\n\n1. length (in bytes)\n2. offset from the beginning of the config section\n3. fundamental type (short, int, str)\n\nContributing\n==============\n\nStroz Friedberg wants to work with the security community to make these open source tools the most comprehensive\navailable for working with Cobalt Strike Beacons. If you encounter a bug, have research to share on Beacons,\nspot a typo in the documentation, want to request new functionality, etc. please submit an issue! If you want to contribute code\nor documentation to the project, please submit a PR and we will review it!  All contributions will be subject to the license included in the repo.\n",
    'author': 'Noah Rubin',
    'author_email': 'noah.rubin@strozfriedberg.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/strozfriedberg/cobaltstrike-config-extractor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
