# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['seckerwiki', 'seckerwiki.commands', 'seckerwiki.scripts']

package_data = \
{'': ['*']}

install_requires = \
['PyInquirer>=1.0.3,<2.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'pdf2image>=1.16.0,<2.0.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['wiki = seckerwiki.wiki:main']}

setup_kwargs = {
    'name': 'seckerwiki',
    'version': '2.0.2',
    'description': 'A collection of scripts used to manage my personal Foam workspace',
    'long_description': "# Seckerwiki Scripts\n\nThis package contains various scripts for managing my markdown-based wiki monorepo.  \nI store everything from lecture notes to journal entries in my wiki.\nThe main command, `wiki`, has functions for downloading slides, setting labels, cross referencing docs and more! see [usage](#usage)\n\n## Installation\n\nDependencies: \n\n- _poppler_ if using a mac (`brew install poppler`)\n- _unoconv_ for converting pptx to pdf ([link](https://github.com/unoconv/unoconv))\n- _gpg_ for journal encryption/decryption\n\nInstall the package & pip dependencies\n\n```\npip install --user seckerwiki\n```\n\n(mac only?) Add the scripts path to your `$PATH` variable, as described in the pip install logs\n\n```shell script\nexport PATH=$PATH:/path/to/wiki/scripts\n```\n\nSet up configuration file\n\n```\nwiki setup\n```\n\nConfigure wiki scripts\n\n```\nvim ~/.personal.yml\n```\n\nSee [config](#config) for configuration file details.\n\n## Wiki structure\n\nI stick to the following wiki structure. Currently, the lecture generation scripts assume this structure.\n\n``` \nwiki_root/\n    Personal/\n        Personal-Management/\n            Journal/\n    Uni/\n        General/\n        Tri-1/\n            COURSE_CODE/\n                Lectures/\n                    images/\n                    lecture-01-name.md\n                Assignments/\n        Tri-2/\n        Full-Year/\n    Scripts/\n```\n\n## Usage\n\nThis section shows off a brief explanation of each command in the wiki script.\n\n### Lecture\n\nInitiates an interactive script for downloading pdf or pptx lecture slides, converts them into individual images, and places \nthe images onto a markdown file.\nMarkdown is a great way to store lecture notes because the plain text format is _simple and reliable_.\nThe images have the content and extra annotations can be written under each slide.\nA version controlled git repository of lecture notes will be around forever.\n\n### Setup\n\nSets up the wiki CLI configuration file with some default values. See [config](#config) for details.\n\n### log \n\nAlias for git log, with some pretty graph options.\n\n### open\n\nruns `[editor] /path/to/wiki`, where `editor` is the editor command, for example `code` (vscode) or `vim`\n\n### commit \n\ndoes a git commit, generating a commit message. If there are a number of staged files, the commit header shows the top level folders instead.\n\n### todo\n\ngrep for TODOs in the wiki.\n\n### sync\n\nperform a `git pull` then `git push`\n\n### tags\n\nTo horizontally group wiki pages in different directories, I implemented a simple _document tagging_ system.\nIn the top line of each file, a comment can be added to add tags in the following format:\n\n```\n<!-- tags: tag1, tag2, tag3 -->\n```\n\nRunning `wiki tags --union` will show all the tags. Running with one or more arguments will reduce the output to files that have _all_ of the tags supplied (alternatively, add the --union tag to show all files that contain _any_ of the supplied tags).\nFor example, `wiki tags todo project` will show all files that have BOTH `todo` and `project` tags.\n\nI have a few things planned to improve this:\n\n- Cache the outputs so it doesn't search the wiki tree each time\n- better visualisation \n- rewrite the function (bit of a mess atm)\n\n### journal\n\nI use my wiki to store encrypted journal entries.\n\nRun `wiki journal` to generate a new empty journal entry in the journal folder specified in the settings. `wiki journal --encrypt` replaces all the `.md` files with `.md.asc` files, encrypting the files with a symmetric key specified in the settings. `wiki journal --decrypt [path]` decrypts a file and prints it to stdout.\n\n### links\n\nopen a list of links in your favourite browser. Great for quickly bringing up most commonly used tabs when you start the computer.\n\n### receipt (WIP)\n\nSave a receipt to the wiki (todo)\n\n### build (WIP)\n\nbuild the markdown into html/pdf files (todo)\n\n## Config\n\nWhen running `wiki setup`, it generates the following example config file (added some comments here to explain the options):\n\n```yaml\nwiki-root: /home/benjamin/Personal/personal # root directory of the wiki\njournal-path: Personal/Personal-Management/Journal # relative path from root to the journal directory\njournal-password: password # symmetric key for encypting journal articles\ncourses: # list of lists of courses separated by semester/trimester\n  tri-1:\n    - COMP424\n    - NWEN438\n    - ENGR401\n  tri-2:\n    - NWEN439\n    - SWEN430\n    - ENGR441\n  full-year:\n    - ENGR489\nlinks: # list of links to open when running the `wiki links` command\n  - https://trello.com/\n  - https://mail.google.com/mail/?shva=1#inbox\n  - https://calendar.google.com/calendar/r\n  - https://clockify.me/tracker\nbrowser-command: firefox # terminal command to open web browser\neditor-command: code # terminal command to open text editor\n```\n\n",
    'author': 'Benjamin Secker',
    'author_email': 'benjamin.secker@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bsecker/wiki/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
