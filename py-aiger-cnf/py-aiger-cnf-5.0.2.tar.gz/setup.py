# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiger_cnf']

package_data = \
{'': ['*']}

install_requires = \
['bidict>=0.21.0,<0.22.0', 'funcy>=1.12,<2.0', 'py-aiger>=6.0.0,<7.0.0']

setup_kwargs = {
    'name': 'py-aiger-cnf',
    'version': '5.0.2',
    'description': 'Python library to convert between AIGER and CNF',
    'long_description': "# py-aiger-cnf\nPython library to convert between AIGER and CNF\n\n[![Build Status](https://cloud.drone.io/api/badges/mvcisback/py-aiger-cnf/status.svg)](https://cloud.drone.io/mvcisback/py-aiger-cnf)\n[![codecov](https://codecov.io/gh/mvcisback/py-aiger-cnf/branch/master/graph/badge.svg)](https://codecov.io/gh/mvcisback/py-aiger-cnf)\n[![PyPI version](https://badge.fury.io/py/py-aiger-cnf.svg)](https://badge.fury.io/py/py-aiger-cnf)\n[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)\n\n<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-generate-toc again -->\n**Table of Contents**\n\n- [Installation](#installation)\n- [Usage](#usage)\n\n<!-- markdown-toc end -->\n\n# Installation\n\nIf you just need to use `aiger_cnf`, you can just run:\n\n`$ pip install py-aiger-cnf`\n\nFor developers, note that this project uses the\n[poetry](https://poetry.eustace.io/) python package/dependency\nmanagement tool. Please familarize yourself with it and then\nrun:\n\n`$ poetry install`\n\n# Usage\n\nThe primary entry point for using `aiger_cnf` is the `aig2cnf`\nfunction which, unsurprisingly, maps `AIG` objects to `CNF` objects.\n\n```python\nimport aiger\nfrom aiger_cnf import aig2cnf\n\nx, y, z = map(aiger.atom, ('x', 'y', 'z'))\nexpr = (x & y) | ~z\ncnf = aig2cnf(expr.aig)\n```\n\nNote that this library also supports `aiger` wrapper libraries so long\nas they export a `.aig` attribute. Thus, could also\nwrite:\n\n```python\ncnf = aig2cnf(expr)\n```\n\n\nThe `CNF` object is a `NamedTuple` with the following three fields:\n\n1. `clauses`: A list of tuples of ints, e.g., `[(1,2,3), (-1,\n   2)]`. Each integer represents a variable's id, with the sign\n   indicating the polarity of the variable.\n2. `input2lit`: A [bidict](https://bidict.readthedocs.io/en/master/)\n   from input names to variable ids.\n2. `output2lit`: A [bidict](https://bidict.readthedocs.io/en/master/)\n   from output names to variable ids.\n",
    'author': 'Marcell Vazquez-Chanlatte',
    'author_email': 'mvc@linux.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mvcisback/py-aiger-cnf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
