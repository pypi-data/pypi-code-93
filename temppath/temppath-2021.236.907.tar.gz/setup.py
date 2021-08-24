# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['temppath']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'temppath',
    'version': '2021.236.907',
    'description': 'A quick way to get a temporary pathlib.Path.',
    'long_description': "# temppath\n\nProvides a quick way to get a `pathlib.Path` file in the system-defined\ntemporary space.  `temppath` does _not_ wrap `tempfile.NamedTemporaryFile`,\nas that automatically deletes on close, and does not allow the same file to be\nwritten, closed, then read [in Windows](https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile),\nwhich is inconsistent with the Unix implementation.  Since `temppath`\nprovides `pathlib.Path` objects, this is not an issue.\n\n## Usage\n\nThere is a nice context manager, which will remove the path for you.\n\n```python\nfrom temppath import TemporaryPathContext\n\nwith TemporaryPathContext() as t:\n    t.write_text('the quick brown fox jumps over the lazy dog')\n    ...\n    do_something_awesome_that_reads(t)\n\n# The file is removed when you leave the `with` context.\n```\n\nYou also have the option to just clean it up yourself if you need more control.\n\n```python\nfrom temppath import TemporaryPath\n\nt = TemporaryPath()\nt.write_text('the quick brown fox jumps over the lazy dog')\n...\ndo_something_awesome_that_reads(t)\n...\nt.unlink()\n```\n",
    'author': 'Bill Allen',
    'author_email': 'billallen256@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/billallen256/temppath',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.4',
}


setup(**setup_kwargs)
