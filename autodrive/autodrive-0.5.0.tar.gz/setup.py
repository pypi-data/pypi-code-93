# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autodrive', 'autodrive.formatting']

package_data = \
{'': ['*']}

install_requires = \
['google-api-python-client-stubs>=1.2.0,<2.0.0',
 'google-api-python-client>=2.0.2,<3.0.0',
 'google-auth-httplib2>=0.1.0,<0.2.0',
 'google-auth-oauthlib>=0.4.3,<0.5.0',
 'jsonlines>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'autodrive',
    'version': '0.5.0',
    'description': 'Simple but robust tool for interacting with the Google Drive and Sheets apis via python.',
    'long_description': '# Autodrive\n\nAutodrive is designed to make it as easy as possible to interact with the Google\nDrive and Sheets APIs via Python. It is especially designed to provide as much\nassistance as possible when writing code through hints and autocompletion, as well\nas via thorough type checking and hinting. These features are currently optimized\nfor VSCode, which you can download <a href="https://code.visualstudio.com/">here</a>\nif you wish. They should also work in other Python IDEs.\n\n---\n\n**Documentation:** https://autodrive-py.readthedocs.io/en/latest/\n\n---\n\n## Requirements\n\n---\n\nPython 3.8+\n\n## Installation\n\n---\n\n### Google API Credentials\n\nFollow the steps outlined in the Prerequisites section\n<a href="https://developers.google.com/drive/api/v3/quickstart/python">here</a>.\nDownload and save the `credentials.json` file to the working directory you want to\nuse Autodrive in.\n\n### First Connection\n\nTo test that your credentials provide the expected connection to your Google Drive\naccount, simply instantiate an Autodrive `Drive` instance:\n\n```\nfrom autodrive import Drive\n\ndrive = Drive()\n```\n\nIf your credentials file was saved as `credentials.json`, your browser should\nautomatically open and prompt you to authorize the GCP project you created to\naccess your Google Drive. Click the various Allow prompts it will show you to\ncomplete your first connection. After you see the browser switch to a page\nindicating you can close the process, you should see a `gdrive_token.json` file\nadded to the working directory you saved your `credentials.json` file in. Next time\nyou use an Autodrive element that needs to connect to your Drive, this token will\nbe used and you will not be prompted to authorize access again until it expires.\n\n## Quickstart\n\n---\n\nThe `Drive` class provides methods for finding and creating objects in your Google\nDrive, such as Folders or Sheets.\n\n```\ngsheet = drive.create_gsheet("my-autodrive-gsheet")\n```\n\n### Finding IDs\n\nIf you use `Drive` to search for your Sheets and Folders, you don\'t need to supply the\nGSheet or Folder IDs yourself, but if you know exactly what Sheet you want, then you\ncan directly instantiate a GSheet or folder by pulling the necessary info from the\nobject\'s url.\n\nFor example, if your Sheet\'s url looks like this:\n\n<p>\ndocs.google.com/spreadsheets/d/19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8/edit#gid=0\n</p>\n\nSimply copy/paste the id (in green, above) between `/d/` and `/edit#` as the\n`gsheet_id`:\n\n```\nfrom autodrive import GSheet\n\ngsheet = GSheet(gsheet_id="19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8")\n```\n\n> **Tabs:** Because Google calls spreadsheets "Sheets", and their api also refers\n> to the individual sub-sheets in a spreadsheet as "Sheets", Autodrive instead\n> refers to them as "Tabs" for clarity.\n\nFor a tab, you can get the `tab_id` from:\n\n<p>\ndocs.google.com/spreadsheets/d/19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8/edit#gid=234276686\n</p>\n\n```\nfrom autodrive import Tab\n\ntab = Tab(\n    gsheet_id="19k5cT9Klw1CA8Sum-olP7C0JUo6_kMiOAKDEeHPiSr8",\n    tab_title="Sheet2",\n    tab_idx=0,\n    tab_id=234276686\n)\n```\n\nFor a folder:\n\n<p>\ndrive.google.com/drive/u/1/folders/1wLx-KMG2jO498xa5ZumB-SEpL-TwczZI\n</p>\n\n```\nfrom autodrive import Folder\n\nfolder = Folder(folder_id="1wLx-KMG2jO498xa5ZumB-SEpL-TwczZI", name="Test Folder")\n```\n\n### Reading and Writing\n\nYou can easily download and write data from a Google Sheet using the `GSheet`,\n`Tab`, or `Range` views.\n\n```\n# Fetches all the data in all cells of the tab:\ntab.get_data()\n\n# Writes 8 cells (2 rows of 4 columns, starting in cell A1) to the tab:\ntab.write_values(\n    [\n        [1, 2, 3, 4],\n        [5, 6, 7, 8],\n    ]\n)\n```\n\n`GSheet` and `Range` have very similar methods, and all of them allow you to read\nand write data to only a specific range in the Google Sheet. See the\n<a href="https://autodrive-py.readthedocs.io/en/latest/">Documentation</a>\nfor more.\n',
    'author': 'Chris Larabee',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chrislarabee/autodrive',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
