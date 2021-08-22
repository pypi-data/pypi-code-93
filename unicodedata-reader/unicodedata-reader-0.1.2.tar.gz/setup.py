# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['unicodedata_reader']

package_data = \
{'': ['*']}

install_requires = \
['platformdirs>=2.2.0,<3.0.0']

setup_kwargs = {
    'name': 'unicodedata-reader',
    'version': '0.1.2',
    'description': '',
    'long_description': '[![CI](https://github.com/kojiishi/unicodedata-reader/actions/workflows/ci.yml/badge.svg)](https://github.com/kojiishi/unicodedata-reader/actions/workflows/ci.yml)\n[![PyPI](https://img.shields.io/pypi/v/unicodedata-reader.svg)](https://pypi.org/project/unicodedata-reader/)\n[![Dependencies](https://badgen.net/github/dependabot/kojiishi/unicodedata-reader)](https://github.com/kojiishi/unicodedata-reader/network/updates)\n\n\n# unicodedata-reader\n\nThis package reads and parses the [Unicode Character Database] files.\n\nMany of them are already in the [unicodedata] module,\nor in other 3rd party modules.\nWhen the desired data is not in any existing modules,\nthis package can read the original data files\nat <https://www.unicode.org/Public/UNIDATA/>.\n\nThis package can also generate JavaScript functions\nthat can read the proprety values of the [Unicode Character Database]\nin browsers.\nPlease see the [JavaScript] section below.\n\n[Unicode Character Database]: https://unicode.org/reports/tr44/\n[unicodedata]: https://docs.python.org/3/library/unicodedata.html\n\n## Install\n\n```sh\npip install unicodedata-reader\n```\nIf you want to clone and install using [poetry]:\n```sh\ngit clone https://github.com/kojiishi/unicodedata-reader\ncd unicodedata-reader\npoetry install\npoetry shell\n```\n\n[poetry]: https://github.com/python-poetry/poetry\n\n\n## Python Usages\n\n```python\nimport unicodedata_reader\n\nreader = unicodedata_reader.UnicodeDataReader.default\nlb = reader.line_break()\nprint(lb.value(0x41))\n```\nThe example above prints `AL`.\nPlease also see [line_break_test.py] for more usages.\n\n[line_break_test.py]: https://github.com/kojiishi/unicodedata-reader/blob/main/tests/line_break_test.py\n\n## JavaScript\n[JavaScript]: #javascript\n\nThe [`UnicodeDataCompressor` class] in this package\ncan generate JavaScript functions that can read the property values\nof the [Unicode Character Database] in browsers.\n\nPlease see [LineBreak.js] for an example of the generated functions\nand [LineBreak.html] for an example usage.\n\n[`UnicodeDataCompressor` class]: https://github.com/kojiishi/unicodedata-reader/blob/main/unicodedata_reader/compressor.py\n[LineBreak.html]: https://github.com/kojiishi/unicodedata-reader/blob/main/js/LineBreak.html\n[LineBreak.js]: https://github.com/kojiishi/unicodedata-reader/blob/main/js/LineBreak.js\n',
    'author': 'Koji Ishii',
    'author_email': 'kojii@chromium.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kojiishi/unicodedata-reader',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
