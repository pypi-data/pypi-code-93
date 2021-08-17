# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['work_components']

package_data = \
{'': ['*']}

modules = \
['work']
entry_points = \
{'console_scripts': ['work = work:main']}

setup_kwargs = {
    'name': 'work-time-log',
    'version': '0.97.4',
    'description': 'Manual time tracking via a CLI that works similarly to git.',
    'long_description': '# Work time log\n\n`work` allows manual time tracking via a CLI that works similarly to `git`:\n\n1. Text files are used for storage. This makes it easy to track the log with `git`.\n2. The `work status` is global, meaning any terminal can be used to check or update it.\n3. Hashes are used to verify that the log was not modified by another tool.\n\n## Release history\n\n- 0.9: Category and message\n    + Entries can now have an optional category and message.\n    + Both can be added when stopping a run or adding an entry.\n    + When listing entries, these fields can be displayed.\n\n## Changelog\n\n- 0.97.4\n    + `list`\n        * `--include-active` now counts active run in total\n        * `--only-time` now merges touching entries for output\n        * `--with-breaks` now shows breaks in separate lines\n    + `switch`: Updated help text for new syntax\n    + `recess`: Clearer error message when removing nonexistent day\n    + completions: Global flags no longer suggested after sub-commands\n    + packaging: Test modules now omitted from package\n',
    'author': 'Valentin',
    'author_email': 'noemail@example.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
