# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['byteparsing']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0']

setup_kwargs = {
    'name': 'byteparsing',
    'version': '0.1.2',
    'description': 'Parser for mixed ASCII/binary data formats',
    'long_description': '# Byteparsing\n\n![Python package](https://github.com/parallelwindfarms/byteparsing/workflows/Python%20package/badge.svg)\n[![PyPI version](https://img.shields.io/pypi/v/byteparsing.svg?colorB=blue)](https://pypi.python.org/pypi/byteparsing/)\n[![codecov](https://codecov.io/gh/parallelwindfarms/byteparsing/graph/badge.svg)](https://codecov.io/gh/parallelwindfarms/byteparsing)\n[![fair-software.eu](https://img.shields.io/badge/fair--software.eu-%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8F%20%20%E2%97%8B-orange)](https://fair-software.eu)\n\nParser for mixed ASCII/binary data. Features:\n\n- Works extremely well with memory-mapped Numpy arrays\n- Included parsers:\n    - OpenFOAM\n\nThe project setup is documented in [a separate\ndocument](project_setup.rst).\nSee also the [extended tutorial](https://parallelwindfarms.github.io/byteparsing/functional.html).\n\n## Installation\n\n### With pip\n\nTo install the latest release of byteparsing, do:\n\n```{.console}\npip install byteparsing\n```\n\n### With GitHub\n\nTo install the latest version of byteparsing, do:\n\n```{.console}\ngit clone https://github.com/parallelwindfarms/byteparsing.git\ncd byteparsing\npip install .\n```\n\nRun tests (including coverage) with:\n\n``` {.console}\npython setup.py test\n```\n\n### Contributing\n\nIf you want to contribute to the development of byteparsing, have a look\nat the [contribution guidelines](CONTRIBUTING.rst).\n\n### License\n\nCopyright (c) 2019, Netherlands eScience Center, University of Groningen\n\nLicensed under the Apache License, Version 2.0 (the \\"License\\"); you\nmay not use this file except in compliance with the License. You may\nobtain a copy of the License at\n\n<http://www.apache.org/licenses/LICENSE-2.0>\n\nUnless required by applicable law or agreed to in writing, software\ndistributed under the License is distributed on an \\"AS IS\\" BASIS,\nWITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\nSee the License for the specific language governing permissions and\nlimitations under the License.\n\n### Credits\n\nThis package was created with\n[Cookiecutter](https://github.com/audreyr/cookiecutter) and the\n[NLeSC/python-template](https://github.com/NLeSC/python-template).\n',
    'author': 'Johan Hidding',
    'author_email': 'j.hidding@esciencecenter.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://parallelwindfarms.github.io/byteparsing',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
