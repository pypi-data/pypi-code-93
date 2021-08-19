# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pelican', 'pelican.plugins.po4a']

package_data = \
{'': ['*']}

install_requires = \
['pelican>=4.5']

setup_kwargs = {
    'name': 'pelican-po4a',
    'version': '0.1.0',
    'description': 'Pelican plugin for managing l10n with po4a',
    'long_description': 'pelican-po4a: Pelican plugin for managing l10n with po4a\n========================================================\n\n<!-- [![Build Status](https://img.shields.io/github/workflow/status/pelican-plugins/po4a/build)](https://github.com/pelican-plugins/po4a/actions) -->\n[![PyPI Version](https://img.shields.io/pypi/v/pelican-po4a)](https://pypi.org/project/pelican-po4a/)\n![License](https://img.shields.io/pypi/l/pelican-po4a?color=blue)\n\nPelican plugin for managing l10n with po4a\n\nInstallation\n------------\n\nThis plugin can be installed via:\n\n    python -m pip install pelican-po4a\n\nUsage\n-----\n\n<<Add plugin details here>>\n\nContributing\n------------\n\nContributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].\n\nTo start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.\n\n[existing issues]: https://edugit.org/Teckids/team-pr/pelican-po4a/-/issues\n[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html\n\nLicense\n-------\n\nThis project is licensed under the Apache-2.0 license.\n',
    'author': 'Dominik George',
    'author_email': 'dominik.george@teckids.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://edugit.org/Teckids/team-pr/pelican-po4a',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
