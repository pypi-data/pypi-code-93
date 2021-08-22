# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['archive_file_urls']

package_data = \
{'': ['*']}

install_requires = \
['archivenow>=2020.7.18,<2021.0.0']

entry_points = \
{'console_scripts': ['archive-file-urls = archive_file_urls.cli:run']}

setup_kwargs = {
    'name': 'archive-file-urls',
    'version': '1.1.1',
    'description': 'Submit URLs listed inside a file to website archival services',
    'long_description': '# archive-file-urls\n\n`archive-file-urls` scans a file for URLs\nand submits them to the [Internet Archive Wayback Machine](https://web.archive.org/)\nin order for them to be archived.\nThe program optionally supports exporting the resulting Internet Archive URLs.\n\nThis is useful in all sorts of situations.\nTake personal blog articles in any format (Markdown, HTML, ...) for example: You can use this program to save the linked web pages.\n\nThe same goes for when you create a LaTex document and want to save the websites cited inside a [BibTeX](http://www.bibtex.org/) file.\n\nAnd of course, there are many more ways to utilize this program.\n\n## Installation\n\n`pip install archive-file-urls`\n\n## Usage\n\n`archive-file-urls --help`\n',
    'author': 'Quoorex',
    'author_email': '46283604+Quoorex@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Quoorex/archive-file-urls',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
