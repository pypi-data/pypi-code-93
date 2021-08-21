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
    'version': '0.1.0',
    'description': '',
    'long_description': '# unicodedata-reader\n\nThis package reads and parses the [Unicode Character Database] files\nat <https://www.unicode.org/Public/UNIDATA/>.\n\nMany of them are already in the [unicodedata] module,\nor in other 3rd party modules.\nWhen the desired data is not in any existing modules,\nthis package can read the original data files.\n\n[Unicode Character Database]: https://unicode.org/reports/tr44/\n[unicodedata]: https://docs.python.org/3/library/unicodedata.html\n\n## Install\n\n```sh\npip install unicodedata-reader\n```\n\n## Python Usages\n\n```python\nfrom unicodedata_reader import UnicodeDataReader\n\nlb = UnicodeDataReader.default.line_break()\nprint(lb.value(0x41))\n```\nThe above example prints `AL`.\nPlease also see [line_break_test.py] for more usages.\n\n[line_break_test.py]: https://github.com/kojiishi/unicodedata-reader/blob/main/tests/line_break_test.py\n\n## JavaScript\n\nThe [`UnicodeDataCompressor` class] in this package\ncan generate JavaScript functions that can read the property values\nof the [Unicode Character Database] in the browsers.\n\nPlease see [u_line_break.js] for an example of the generated functions\nand [u_line_break.html] for an example usage.\n\n[`UnicodeDataCompressor` class]: https://github.com/kojiishi/unicodedata-reader/blob/main/unicodedata_reader/compressor.py\n[u_line_break.html]: https://github.com/kojiishi/unicodedata-reader/blob/main/js/u_line_break.html\n[u_line_break.js]: https://github.com/kojiishi/unicodedata-reader/blob/main/js/u_line_break.js\n',
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
