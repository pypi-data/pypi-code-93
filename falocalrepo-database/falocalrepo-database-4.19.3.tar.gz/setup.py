# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['falocalrepo_database']

package_data = \
{'': ['*']}

install_requires = \
['chardet>=4.0.0,<5.0.0', 'filetype>=1.0.7,<2.0.0', 'psutil>=5.8.0,<6.0.0']

setup_kwargs = {
    'name': 'falocalrepo-database',
    'version': '4.19.3',
    'description': 'Database functionality for falocalrepo.',
    'long_description': '# FALocalRepo-Database\n\n[![version_pypi](https://img.shields.io/pypi/v/falocalrepo-database?logo=pypi)](https://pypi.org/project/falocalrepo-database/)\n[![version_gitlab](https://img.shields.io/badge/dynamic/json?logo=gitlab&color=orange&label=gitlab&query=%24%5B%3A1%5D.name&url=https%3A%2F%2Fgitlab.com%2Fapi%2Fv4%2Fprojects%2Fmatteocampinoti94%252Ffalocalrepo-database%2Frepository%2Ftags)](https://gitlab.com/MatteoCampinoti94/falocalrepo-database)\n[![version_python](https://img.shields.io/pypi/pyversions/falocalrepo-database?logo=Python)](https://www.python.org)\n\nDatabase functionality for [falocalrepo](https://gitlab.com/MatteoCampinoti94/falocalrepo).\n\n## Usage\n\n_Detailed usage and components documentation will be added in a future patch_\n\n## Tables\n\nTo store its information, the database uses four tables: `SETTINGS`, `USERS`, `SUBMISSIONS` and `JOURNALS`.\n\n**Note**: bar-separated lists are formatted as `|item1||item2|` to properly isolate all elements\n\n### Settings\n\nThe settings table contains settings for the program and statistics of the database.\n\n* `HISTORY` list of executed commands in the format `[[<time1>, "<command1>"], ..., [<timeN>, "<commandN>"]]` (UNIX time\n  in seconds)\n* `COOKIES` cookies for the scraper, stored in JSON format\n* `FILESFOLDER` location of downloaded submission files\n* `VERSION` database version\n\n### Users\n\nThe users table contains a list of all the users that have been download with the program, the folders that have been\ndownloaded, and the submissions found in each of those.\n\nEach entry contains the following fields:\n\n* `USERNAME` The URL username of the user (no underscores or spaces)\n* `FOLDERS` the folders downloaded for that specific user, sorted and bar-separated\n\n### Submissions\n\nThe submissions table contains the metadata of the submissions downloaded by the program and information on their files\n\n* `ID` the id of the submission\n* `AUTHOR` the username of the author (uploader) in full format\n* `TITLE`\n* `DATE` upload date in ISO format YYYY-MM-DD**T**HH:MM\n* `DESCRIPTION` description in html format\n* `TAGS` bar-separated tags\n* `CATEGORY`\n* `SPECIES`\n* `GENDER`\n* `RATING`\n* `TYPE` image, text, music, or flash\n* `FILEURL` the remote URL of the submission file\n* `FILEEXT` the extensions of the downloaded file. Can be empty if the file contained errors and could not be recognised\n  upon download\n* `FILESAVED` file and thumbnail download status: 00, 01, 10, 11. 1*x* if the file was downloaded 0*x* if not, *x*1 if\n  thumbnail was downloaded, *x*0 if not\n* `FAVORITE` a bar-separated list of users that have "faved" the submission\n* `MENTIONS` a bar-separated list of users that are mentioned in the submission description as links\n* `FOLDER` the folder of the submission (`gallery` or `scraps`)\n* `USERUPDATE` whether the submission was added as a user update or favorite/single entry\n\n### Journals\n\nThe journals table contains the metadata of the journals downloaded by the program.\n\n* `ID` the id of the journal\n* `AUTHOR` the username of the author (uploader) in full format\n* `TITLE`\n* `DATE` upload date in ISO format YYYY-MM-DD**T**HH:MM\n* `CONTENT` content in html format\n* `MENTIONS` a bar-separated list of users that are mentioned in the journal content as links\n* `USERUPDATE` whether the journal was added as a user update or single entry\n\n## Submission Files\n\nThe `save_submission` functions saves the submission metadata in the database and stores the files.\n\nSubmission files are saved in a tiered tree structure based on their submission ID. IDs are zero-padded to 10 digits and\nthen broken up in 5 segments of 2 digits; each of these segments represents a folder tha will be created in the tree.\n\nFor example, a submission `1457893` will be padded to `0001457893` and divided into `00`, `01`, `45`, `78`, `93`. The\nsubmission file will then be saved as `00/01/45/78/93/submission.file` with the correct extension extracted from the\nfile itself - FurAffinity links do not always contain the right extension and often confuse jpg and png.\n\n## Upgrading Database\n\nThe `FADatabase.upgrade` function allows to upgrade the database to the current version.\n\n_Note:_ Versions before 2.7.0 are not supported by falocalrepo-database version 3.0.0 and above. To update from those to\nthe new version use [falocalrepo](https://gitlab.com/MatteoCampinoti94/FALocalRepo/-/releases/v2.11.2) version 2.11.2 to\nupdate the database to version 2.7.0\n',
    'author': 'Matteo Campinoti',
    'author_email': 'matteo.campinoti94@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/MatteoCampinoti94/falocalrepo-database',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
