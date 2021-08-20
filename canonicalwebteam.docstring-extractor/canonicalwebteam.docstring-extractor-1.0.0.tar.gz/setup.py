# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['canonicalwebteam', 'canonicalwebteam.docstring_extractor']

package_data = \
{'': ['*']}

install_requires = \
['docstring-parser>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'canonicalwebteam.docstring-extractor',
    'version': '1.0.0',
    'description': 'Get Python docstrings from files',
    'long_description': '# docstring-extractor\n\nThis library allows parsing docstrings of an entire Python file. It uses [ast](https://docs.python.org/3/library/ast.html) and [docstring-parser](https://github.com/rr-/docstring_parser).\n\nThe main difference between this library and docstring-parser is that this one is able to parse entire Python files.\n\n## Installation:\n`pip install docstring-extractor`\n\n## Usage\n\n```python\n>>> from canonicalwebteam.docstring_extractor import get_docstrings\n>>>\n>>> with open("example.py") as file:\n...     docstrings = get_docstrings(file)\n```\n\nImaging you have the following Python code:\n```python\n"""\nExample module.\n\nLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod\ntempor incididunt ut labore et dolore magna aliqua.\n"""\n\n\ndef test_function():\n    """\n    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod\n    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim\n    veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea\n    commodo consequat. Duis aute irure dolor in reprehenderit in voluptate\n    velit esse cillum dolore eu fugiat nulla pariatur.\n\n    Parameters:\n        a (int): A decimal integer\n        b (int): Another decimal integer\n\n    Returns:\n        str: A string containing "foo"\n    """\n    return "foo"\n```\n\nThe output of the `get_docstrings` function will be the following dict object:\n\n```python\n{\'type\': \'Module\',\n \'name\': \'example\',\n \'line\': 0,\n \'docstring\': <docstring_parser.common.Docstring at 0x7f06adee7a00>,\n \'docstring_text\': \'Example module.\\n\\nLorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod\\ntempor incididunt ut labore et dolore magna aliqua.\',\n \'content\': [\n    {\'type\': \'Function\',\n       \'name\': \'test_function\',\n       \'line\': 9,\n       \'docstring\': <docstring_parser.common.Docstring at 0x7f06adef7490>,\n       \'docstring_text\': \'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod\\ntempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim\\nveniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea\\ncommodo consequat. Duis aute irure dolor in reprehenderit in voluptate\\nvelit esse cillum dolore eu fugiat nulla pariatur.\\n\\nParameters:\\n    a (int): A decimal integer\\n    b (int): Another decimal integer\\n\\nReturns:\\n    str: A string containing "foo"\',\n    \'content\': []\n    }\n ]\n}\n```\n\nYou can see the different properties of the Docstring object [here](https://github.com/rr-/docstring_parser/blob/master/docstring_parser/common.py), as an example if you are interested in obtaining the return type and return description of the first function:\n\n```python\n>>> docstrings["content"][0]["docstring"].returns.type_name\n\'str\'\n>>> docstrings["content"][0]["docstring"].returns.description\n\'A string containing "foo"\'\n```\n',
    'author': 'Canonical Web Team',
    'author_email': 'webteam@canonical.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/canonical-web-and-design/canonicalwebteam.docstring-extractor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
