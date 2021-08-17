# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['synr']

package_data = \
{'': ['*']}

install_requires = \
['attrs']

setup_kwargs = {
    'name': 'synr',
    'version': '0.3.1',
    'description': 'A consistent AST for Python',
    'long_description': "# Synr\n\nSynr is a library that provides a stable Abstract Syntax Tree for Python.\n\n## Features\n\n- The Synr AST does not change between Python versions.\n- Every AST node contains line and column information.\n- There is a single AST node for assignments (compared to three in Python's ast module).\n- Support for returning multiple errors at once.\n- Support for custom error reporting.\n\n## Usage\n\n```python\nimport synr\n\ndef test_program(x: int):\n  return x + 2\n\n# Parse a Python function into an AST\nast = synr.to_ast(test_program, synr.PrinterDiagnosticContext())\n```\n\n## Documentation\n\nPlease see [https://synr.readthedocs.io/en/latest/](https://synr.readthedocs.io/en/latest/) for documentation.\n",
    'author': 'Jared Roesch',
    'author_email': 'jroesch@octoml.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
