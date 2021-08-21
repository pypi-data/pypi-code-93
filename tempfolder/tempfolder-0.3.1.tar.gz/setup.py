# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tempfolder']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'tempfolder',
    'version': '0.3.1',
    'description': "🗂 Easily create temporary folders, add files into them and don't worry about deleting them, tempfolder will take care",
    'long_description': "[![Coverage Status](https://coveralls.io/repos/github/jalvaradosegura/tempfolder/badge.svg?branch=main)](https://coveralls.io/github/jalvaradosegura/tempfolder?branch=main)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![basic-quality-check](https://github.com/jalvaradosegura/tempfolder/actions/workflows/code_quality.yml/badge.svg)](https://github.com/jalvaradosegura/tempfolder/actions/workflows/code_quality.yml)\n[![GitHub license](https://img.shields.io/github/license/jalvaradosegura/tempfolder)](https://github.com/jalvaradosegura/tempfolder/blob/main/LICENSE)\n\n# tempfolder\n🗂 Easily create temporary folders, add files into them and don't worry about deleting them, tempfolder will take care\n\n## Installation\ntempfolder is published on [PyPI](https://pypi.org/project/tempfolder/) and can be installed from there:\n```\npip install tempfolder\n```\n\n## Usage\nLet's see a case in which we want to test a function that creates a file inside a folder\n```py\nfrom pathlib import Path\nfrom tempfolder import use_temp_folder\n\n\n# A function that create a file inside a folder\ndef add_config_file_to_folder(folder: str):\n    with open(Path(folder) / 'config.cfg', 'w') as f:\n        f.write('i-like: tempfolder')\n\n\n# Name of the temporary folder\nTEMP_FOLDER = Path('temp_folder')\n\n\n# Test the function\n@use_temp_folder(TEMP_FOLDER)\ndef test_add_config_file_to_folder():\n    add_config_file_to_folder(TEMP_FOLDER)\n    assert TEMP_FOLDER.exists()\n\n\n# Check that the temporary folder was deleted\nassert not TEMP_FOLDER.exists()\n```\nRun with pytest:\n```\n========= 1 passed in 0.05s =========\n```\n\nIf we remove the decorator from the previous code and run the test, we get:\n```py\nfrom pathlib import Path\n\n\n# A function that create a file inside a folder\ndef add_config_file_to_folder(folder: str):\n    with open(Path(folder) / 'config.cfg', 'w') as f:\n        f.write('i-like: tempfolder')\n\n\n# Name of the temporary folder\nTEMP_FOLDER = Path('temp_folder')\n\n\n# Test the function, now with no decorator\ndef test_add_config_file_to_folder():\n    add_config_file_to_folder(TEMP_FOLDER)\n    assert TEMP_FOLDER.exists()\n```\nTest:\n```sh\n> with open(Path(folder) / 'config.cfg', 'w') as f:\nE FileNotFoundError: [Errno 2] No such file or directory: 'temp_folder/config.cfg'\n```\nAs you can see the folder wasn't even created, because tempfolder is the one who takes care of the creation and deletion of your temporary folders (and its files).\n",
    'author': 'Jorge Alvarado',
    'author_email': 'alvaradosegurajorge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jalvaradosegura/tempfolder',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
