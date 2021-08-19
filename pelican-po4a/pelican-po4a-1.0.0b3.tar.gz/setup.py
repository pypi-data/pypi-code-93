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
    'version': '1.0.0b3',
    'description': 'Pelican plugin for managing l10n with po4a',
    'long_description': 'pelican-po4a: Pelican plugin for managing l10n with po4a\n========================================================\n\n<!-- [![Build Status](https://img.shields.io/github/workflow/status/pelican-plugins/po4a/build)](https://github.com/pelican-plugins/po4a/actions) -->\n[![PyPI Version](https://img.shields.io/pypi/v/pelican-po4a)](https://pypi.org/project/pelican-po4a/)\n![License](https://img.shields.io/pypi/l/pelican-po4a?color=blue)\n\nPelican plugin for managing l10n with po4a\n\nFeatures and limitations\n------------------------\n\nThis plugin is intended to help with integrating [po4a](https://po4a.org) into the Pelican\nbuild process. With po4a, it is possible to translate entire content files using any gettext\ntool, e.g. [Weblate](https://weblate.org).\n\nThe plugin does the following:\n\n * Track content files and their translation counterparts to build the\n   source/translation list in `po4a.conf`\n * Support the generic `$lang` pattern for po4a.conf source/translation sets\n * Write a `po4a.conf` file matching Pelican settings and content\n * Update message catalogs based on source files\n * Update translations based on message catalogs\n\nThe plugin supports the following other plugins:\n\n * [i18n_subsites](https://github.com/getpelican/pelican-plugins/tree/master/i18n_subsites) –\n   the po4a plugin only acts on the main language and writes data once\n * [jinja2content](https://github.com/getpelican/pelican-plugins/tree/master/jinja2content) –\n   the wrapped readers are detected for content format detection\n * [asciidoc_readers](https://github.com/getpelican/pelican-plugins/tree/master/asciidoc_reader) –\n   reader is supported and detected for content format detection\n\nCurrently, the plugin has the following limitations:\n\n * If anything changed (source content for main language or translations), the build has\n   to be run twice (a `CRITICAL` message is emitted to notify the user). This is because\n   we have no control over the order in which languages are built, and translated sites (\n   when using `i18n_subsites`) might be built before translations are picked up\n * `jinja2content` blocks and vanilla HTML blocks in Markdown are not handled by po4a,\n   they are added to the catalogs verbatim\n * Markdown files need to have separators around metadata (frontmatter) sections, because\n   po4a requires them\n\nPatches welcome!\n\nInstallation\n------------\n\nThis plugin can be installed via:\n\n    python -m pip install pelican-po4a\n\nAfter doing that, append `po4a` to your `PLUGINS` setting.\n\nObviously, you also need to have `po4a` itself installed.\n\nUsage\n-----\n\nThe following settings are available:\n\n| Setting              | Description                                    | Default                           |\n|----------------------|------------------------------------------------|-----------------------------------|\n| `PO4A_CONF`          | (Relative) path to `po4a.conf` file            | `./po4a.conf`                     |\n| `PO4A_PO_DIR`        | (Relative) path to the catalog directory       | `./po`                            |\n| `PO4A_CATALOG`       | Name of the message catalog                    | `pelican-website`                 |\n| `PO4A_PAGE_PATTERN`  | Generic pattern for translation paths of pages | `content/pages/{lang}/{relpath}`  |\n| `PO4A_POST_PATTERN`  | Generic pattern for translation paths of posts | `content/posts/{lang}/{relpath}`  |\n\nAll necessary po4a actions are automatically taken when building the main site language.\nIf changes were made, a `CRITICAL` message is logged, and starting the build again is required\n(cf. limitations).\n\nContributing\n------------\n\nContributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].\n\nTo start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.\n\n[existing issues]: https://edugit.org/Teckids/team-pr/pelican-po4a/-/issues\n[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html\n\nLicense\n-------\n\nThis project is licensed under the Apache-2.0 license.\n',
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
