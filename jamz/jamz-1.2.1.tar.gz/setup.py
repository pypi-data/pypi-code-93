# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jamz']

package_data = \
{'': ['*']}

install_requires = \
['mutagen>=1.45.1,<2.0.0', 'tabulate>=0.8.9,<0.9.0']

entry_points = \
{'console_scripts': ['jamz = jamz.jamz:main']}

setup_kwargs = {
    'name': 'jamz',
    'version': '1.2.1',
    'description': 'Renames music files based on their tags',
    'long_description': '# Jamz\n\nJamz is a small command-line utility for renaming music files based on their tags.\n\nFor example, if you run:\n\n`jamz ~/Music/Nirvana/Nevermind/ \'{jamz_padded_tracknumber} - {title}.flac\'`\n\nYour Nevermind songs will now be named:\n\n```txt\n01 - Smells Like Teen Spirit.flac\n02 - In Bloom.flac\n03 - Come as You Are.flac\n...\n12 - Something in the Way / Endless, Nameless.flac\n```\n\n## Installation\n\n`pip install jamz`\n\n## Usage\n\nJamz takes two positional arguments, the directory to rename files in, and the template with which to rename them.\nFor the template, Jamz passes all the tags from each file as formatting arguments, so you can use any tag in your template that the filetype supports.\nFor example, when working with files that use the Vorbis comment format (FLAC, Ogg, etc.), you can use TITLE, ALBUM, DATE, etc. in your template.\n\n`jamz /mymusic/ \'{ARTIST} - {TITLE} - {TRACKNUMBER}.ogg\'`\n\n(Note: for this format specifically, jamz also supports using the lowercase version of each tag, e.g. "title")\n\n### Special Tags\n\nJamz also adds a few special tags of its own. Every Jamz special tag starts with `jamz`.\n\n`jamz_padded_tracknumber`: The tracknumber (if found) padded to two digits (e.g. `2` -> `02`)\n\n`jamz_original_suffix`: The original suffix of the file, e.g. `.flac` if the file is named `song.flac`.\n\n### Flags\n\n```txt\n-r, --recursive      Recursively descend the file tree\n-d, --dry-run        Print the new names of the files, but don\'t actually rename them\n-i, --ignore-errors  Skip over files that lead to errors\n-v, --verbose        Enable verbose logging\n```\n\n## Technical Details\n\nJamz uses [Mutagen](https://mutagen.readthedocs.io/en/latest/) to read tags.\nAll non-special tags available for use in templates come from the Mutagen tags object.\nBecause Mutagen supports multiple tags per key, Jamz assumes the first value is canonical, and passes only that one to the template.\n',
    'author': 'Harry',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/heldridge/jamz',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
