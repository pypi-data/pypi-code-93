# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['htmlclasses', 'htmlclasses.lib']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'htmlclasses',
    'version': '0.3.1',
    'description': 'Python in, HTML out.',
    'long_description': '# htmlclasses\n\nPython in, HTML out.\n\nThere are templating engines making it possible to write code\nin HTML template files. However, I would very much prefer\nto be able to write Python that gets converted to HTML \nrather than write Python-like mini language engulfed in HTML. \n\n## Version\n\n0.3.1\n\n## Goals\n\nGenerating valid HTML from pure Python code.\n\n## Non-goals\n\nFeatures geared toward JavaScript.\n\n1. I find using 2 intertwined languages too cumbersome.\n2. JavaScript is heavily overused and misused.\n   I don\'t want to add to the problem.\n\n\n## Installation\n\n`pip install htmlclasses`\n\n## Developing\n\nThis project is managed with poetry: https://github.com/python-poetry/poetry\n\n1. `git clone git@github.com:uigctaw/htmlclasses.git`\n2. `poetry install`\n\n### Running tests\n\n`./check_all.sh`\n\n## Examples\n\nTo convert Python to HTML run:\n\n```python\nfrom htmlclasses import to_string\n\nto_string(html, indent=\'    \')\n```\n\n### Hello World\n\n```python\nfrom htmlclasses import E\n\n\nclass html(E):\n\n    class head:\n        pass\n\n    class body:\n\n        class p:\n\n            TEXT = \'Hello, world!\'\n```\n\n```html\n<!DOCTYPE html>\n<html>\n    <head/>\n    <body>\n        <p>\n            Hello, world!\n        </p>\n    </body>\n</html>\n```\n\n### Repeated Elements\n\n```python\nfrom htmlclasses import E\n\n\nclass html(E):\n\n    class head(E):  # Must sublcass if repeating tags\n\n        class meta:\n            name = \'description\'\n            content = \'Framework usage examples\'\n\n        class meta:  # type: ignore[no-redef]  # noqa: F811\n            name = \'keywords\'\n            content = \'Python, HTML\'\n\n    class body:\n\n        class p:\n\n            TEXT = \'Hello, world!\'\n```\n\n```html\n<!DOCTYPE html>\n<html>\n    <head>\n        <meta name="description" content="Framework usage examples"/>\n        <meta name="keywords" content="Python, HTML"/>\n    </head>\n    <body>\n        <p>\n            Hello, world!\n        </p>\n    </body>\n</html>\n```\n\n## Work in progress\n\nSVG utilities for creating plots.\n\n## Alternatives\n\nhttps://pypi.org/project/html\n',
    'author': 'uigctaw',
    'author_email': 'uigctaw@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/uigctaw/htmlclasses',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
