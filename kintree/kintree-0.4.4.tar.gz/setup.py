# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kintree',
 'kintree.common',
 'kintree.config',
 'kintree.database',
 'kintree.kicad',
 'kintree.search',
 'kintree.search.mouser',
 'kintree.wrapt_timeout_decorator']

package_data = \
{'': ['*'],
 'kintree.config': ['digikey/*',
                    'inventree/*',
                    'kicad/*',
                    'lcsc/*',
                    'mouser/*',
                    'search/*',
                    'settings/*'],
 'kintree.kicad': ['templates/*', 'templates_project/*']}

install_requires = \
['PySimpleGUI>=4.28.0,<5.0',
 'PyYAML>=5.3.1,<6.0',
 'digikey-api>=0.5.0,<1.0',
 'fuzzywuzzy>=0.18.0,<1.0',
 'inventree>=0.4.4,<1.0',
 'multiprocess>=0.70.12.2,<0.71',
 'python-Levenshtein>=0.12.2,<0.13.0',
 'validators>=0.18.2',
 'wrapt>=1.12.1,<2.0']

entry_points = \
{'console_scripts': ['kintree = kintree:kintree_gui.main',
                     'kintree_setup_inventree = kintree:setup_inventree.main']}

setup_kwargs = {
    'name': 'kintree',
    'version': '0.4.4',
    'description': 'Fast part creation in KiCad and InvenTree',
    'long_description': '# Ki-nTree\n### Fast part creation in [KiCad](https://kicad-pcb.org/) and [InvenTree](https://inventree.readthedocs.io/) \n[![License: GPL v3.0](https://img.shields.io/badge/license-GPL_v3.0-green.svg)](https://www.gnu.org/licenses/gpl-3.0)\n[![Python Versions](https://raw.githubusercontent.com/sparkmicro/Ki-nTree/master/images/python_versions.svg)](https://www.python.org/)\n[![PyPI](https://img.shields.io/pypi/v/kintree)](https://pypi.org/project/kintree/)\n[![Tests | Linting | Publishing](https://github.com/sparkmicro/Ki-nTree/actions/workflows/test_deploy.yaml/badge.svg)](https://github.com/sparkmicro/Ki-nTree/actions)\n[![Coverage Status](https://coveralls.io/repos/github/sparkmicro/Ki-nTree/badge.svg?branch=master&service=github)](https://coveralls.io/github/sparkmicro/Ki-nTree?branch=master)\n\n## Demo Videos :fast_forward: [Full Demo](https://youtu.be/haSAu926BOI) :fast_forward: [KiCad Demo](https://youtu.be/NSMfCCD0uVw)\n\n<img src="https://raw.githubusercontent.com/sparkmicro/Ki-nTree/master/images/doc/kintree_example.png"  width="auto" height="auto">\n\n## Introduction\nKi-nTree (pronounced "Key Entry" or "Key \'n\' Tree") aims to:\n* automate part creation of KiCad library parts\n* automate part creation of InvenTree parts\n* synchronize parts data between KiCad and InvenTree\n\nKi-nTree works with:\n- [Digi-Key](https://developer.digikey.com/), [Mouser](https://www.mouser.com/api-hub/) and [LCSC](https://lcsc.com/) **enormous** part databases and free APIs\n- the awesome open-source [Digi-Key API python library](https://github.com/peeter123/digikey-api) built and maintained by [@peeter123](https://github.com/peeter123)\n- the awesome open-source [InvenTree Inventory Management System](https://github.com/inventree/inventree) built and maintained by [@SchrodingersGat](https://github.com/SchrodingersGat)\n- [KiCad](https://kicad-pcb.org/) (of course!) and their open-source [library utils](https://github.com/KiCad/kicad-library-utils)\n\nKi-nTree was developped by [@eeintech](https://github.com/eeintech) for [SPARK Microsystems](https://www.sparkmicro.com/), who generously accepted to make it open-source!\n\n## Get Started\n\n### Requirements\n\n* Ki-nTree is currently tested for Python 3.7 to 3.9 versions.\n* Ki-nTree requires a Digi-Key **production** API instance. To create one, go to https://developer.digikey.com/. Create an account, an organization and add a **production** API to your organization. Save both Client ID and Secret keys.\n> [Here is a video](https://youtu.be/OI1EGEc0Ju0) to help with the different steps\n* Ki-nTree requires a Mouser Search API key. To request one, head over to https://www.mouser.ca/api-search/ and click on "Sign Up for Search API"\n\n### Installation (system wide)\n\n1. Install using Pip\n\n``` bash\n$ pip install -U kintree\n```\n\n2. Run Ki-nTree\n\n``` bash\n$ kintree\n```\n\n### Run in virtual environment (contained)\n\n##### Linux / MacOS\n\nCreate a virtual environment and activate it with:\n\n``` bash\n$ python3 -m venv env-kintree\n$ source env-kintree/bin/activate\n```\n\nThen follow the steps from the [installation section](#installation-system-wide).\n\n##### Windows\n\nIn Git Bash, use the following commands to create and activate a virtual environment:\n``` bash\n$ python3 -m venv env-kintree\n$ source env-kintree/Scripts/activate\n```\nFor any other Windows terminal, refer to the [official documentation](https://docs.python.org/library/venv.html#creating-virtual-environments)\n\n### Packages\n#### Arch Linux\n\nKi-nTree is [available on Arch Linux\'s AUR](https://aur.archlinux.org/packages/python-kintree/) as `python-kintree`.\n\n### Usage Instructions\n\n#### Settings\n1. With Ki-nTree GUI open, click on "Settings > Digi-Key" and fill in both Digi-Key API Client ID and Secret keys (optional: click on "Test" to [get an API token](#get-digi-key-api-token))\n2. Click on "Settings > Mouser" and fill in the Mouser part search API key\n3. Click on "Settings > KiCad", browse to the location where KiCad symbol and footprint libraries are stored on your computer then click "Save"\n4. If you intend to use InvenTree with this tool, click on "Settings > InvenTree" and fill in your InvenTree server address and credentials then click "Save" (optional: click on "Test" to get an API token)\n\n#### Get Digi-Key API token\n<details>\n<summary>Show steps (click to expand)</summary>\n<p>\n\nEnter your Digi-Key developper account credentials then login. The following page will appear (`user@email.com` will show your email address):\n\n<img src="https://raw.githubusercontent.com/sparkmicro/Ki-nTree/master/images/doc/digikey_api_approval_request.png" width="600" height="auto">\n\nClick on "Allow", another page will open.  \nClick on the "Advanced" button, then click on "Proceed to localhost (unsafe)" at the bottom of the page:\n\n<img src="https://raw.githubusercontent.com/sparkmicro/Ki-nTree/master/images/doc/digikey_api_approval_request2.png"  width="600" height="auto">\n\n> On Chrome, if the "Proceed to localhost (unsafe)" link does not appear, enable the following flag: [chrome://flags/#allow-insecure-localhost](chrome://flags/#allow-insecure-localhost)\n\nLastly, a new page will open with a "You may now close this window." message, proceed to get the token.\n\n</p>\n</details>\n\n#### Part Number Search\n\nKi-nTree currently supports APIs for the following electronics suppliers: Digi-Key, Mouser and LCSC.\n\n1. In the main window, enter the part number and select the supplier in drop-down list, then click "CREATE". It will start by fetching part data using the supplier\'s API\n2. In the case Digi-Key has been selected and the API token is not found or expired, a browser window will pop-up. To get a new token: [follow those steps](#get-digi-key-api-token)\n3. Once the part data has been successfully fetched from the supplier\'s API, you will be prompted to add/confirm/edit the part information, followed by the `Category` and `Subcategory` to use for this part (Ki-nTree tries to match them automatically)\n4. Then, you will be prompted with selecting the KiCad symbol library, template and footprint library to use for this part\n5. It will take some time to complete the part creation in InvenTree and/or KiCad, once it finishes you\'ll be notified of the result  \n6. Finally, if the part was created or found in InvenTree, your browser will automatically open a new tab with the part information\n\nEnjoy!\n\n*For any problem/bug you find, please [report an issue](https://github.com/sparkmicro/Ki-nTree/issues).*\n\n## Development\n\n### Requirements\n\nYou need `python>=3.7` and `poetry`.\n\nYou can install poetry by following the instructions [on its official\nwebsite](https://python-poetry.org/docs/master/#installation), by using `pip\ninstall poetry` or by installing a package on your Linux distro.\n\n### Setup and run\n1. Clone this repository\n``` bash\n$ git clone https://github.com/sparkmicro/Ki-nTree\n```\n\n2. Install the requirements into a `poetry`-managed virtual environment\n``` bash\n$ poetry install\nInstalling dependencies from lock file\n...\nInstalling the current project: kintree (0.1.0)\n```\n> Note: the version is not accurate (placeholder only)\n\n3. Run Ki-nTree in the virtual environment\n```bash\n$ poetry run python -m kintree.kintree_gui\n```\nor\n\n```bash\n$ poetry shell\n$ python -m kintree.kintree_gui\n```\n\n#### Build\n1. Make sure you followed the previous installation steps, then run:\n``` bash\n$ poetry build\n```\n\nYou will get a message similar to this:\n\n```\nBuilding kintree (0.3.10)\n  - Building sdist\n  - Built kintree-0.3.10.tar.gz\n  - Building wheel\n  - Built kintree-0.3.10-py3-none-any.whl\n```\n2. Exit the virtual environment (`Ctrl + D` on Linux; you can also close the\n   terminal and reopen it in the same folder).\n\n   Run `pip install dist/<wheel_file>.whl` with the file name from the previous\n   step. For example:\n\n```bash\npip install dist/kintree-0.3.10-py3-none-any.whl\n```\n\n3. You can now start Ki-nTree by typing `kintree` in the terminal, provided\n   that your python dist path is a part of your `$PATH`.\n\n## Roadmap\n\n#### Versions 0.4.x or later\n##### Global\n\n- Support other suppliers like LCSC and Mouser ([Ref #50](https://github.com/sparkmicro/Ki-nTree/issues/50))\n- Allow user to decide the category code to use for IPN\n- Add "Synchronize" menu option to pull InvenTree parts data into KiCad\n- Fetch Digi-Key price breakdown and add it to Supplier Part (InvenTree)\n- Add option to add as alternate (supplier part) to existing part\n- Document configuration and backend\n\n##### GUI\n\n- Move to PySide2? ([Ref #37](https://github.com/sparkmicro/Ki-nTree/issues/37))\n- Add icon to GUI (not successful using PySimpleGUI)\n- Create loading animation for API searches (asyncio)\n',
    'author': 'eeintech',
    'author_email': 'eeintech@eeinte.ch',
    'maintainer': 'eeintech',
    'maintainer_email': 'eeintech@eeinte.ch',
    'url': 'https://github.com/sparkmicro/Ki-nTree',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
