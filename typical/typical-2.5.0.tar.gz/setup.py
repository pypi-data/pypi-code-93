# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['typic',
 'typic.constraints',
 'typic.ext',
 'typic.ext.schema',
 'typic.serde',
 'typic.types']

package_data = \
{'': ['*']}

install_requires = \
['future-typing>=0.4.1,<0.5.0', 'inflection>=0.5,<0.6', 'pendulum>=2.1,<3.0']

extras_require = \
{'benchmarks': ['sqlalchemy>=1.3.13,<2.0.0',
                'pytest-benchmark[histogram]>=3.2,<4.0',
                'marshmallow>=3.2,<4.0',
                'toastedmarshmallow>=2.15,<3.0',
                'djangorestframework>=3.10,<4.0',
                'pydantic[email]>=1.0,<2.0',
                'pydantic[email]>=1.0,<2.0',
                'django>=2.2,<3.0'],
 'docs': ['mkdocs>=1.1,<2.0',
          'mkdocs-material>=5.5,<6.0',
          'mkdocs-awesome-pages-plugin>=2.2.1,<3.0.0',
          'pymdown-extensions>=7.0,<8.0'],
 'json': ['ujson>=2.0'],
 'lint': ['flake8>=3.7.9,<4.0.0',
          'mypy>=0.910,<0.911',
          'black>=21,<22',
          'types-python-dateutil',
          'types-setuptools',
          'types-toml',
          'types-typed-ast',
          'types-ujson'],
 'schema': ['fastjsonschema>=2.14,<3.0'],
 'tests': ['fastjsonschema>=2.14,<3.0',
           'ujson>=2.0',
           'pytest>=6.2,<7.0',
           'pytest-cov>=2.8,<3.0',
           'sqlalchemy>=1.3.13,<2.0.0',
           'pydantic[email]>=1.0,<2.0',
           'mypy>=0.910,<0.911'],
 'tests:python_version >= "3.7.1" and python_version <= "3.9"': ['pandas>=1.1.3,<2.0.0']}

setup_kwargs = {
    'name': 'typical',
    'version': '2.5.0',
    'description': "Typical: Python's Typing Toolkit.",
    'long_description': '# typical: Python\'s Typing Toolkit\n[![image](https://img.shields.io/pypi/v/typical.svg)](https://pypi.org/project/typical/)\n[![image](https://img.shields.io/pypi/l/typical.svg)](https://pypi.org/project/typical/)\n[![image](https://img.shields.io/pypi/pyversions/typical.svg)](https://pypi.org/project/typical/)\n[![image](https://img.shields.io/github/languages/code-size/seandstewart/typical.svg?style=flat)](https://github.com/seandstewart/typical)\n[![Test & Lint](https://github.com/seandstewart/typical/workflows/Test%20&%20Lint/badge.svg)](https://github.com/seandstewart/typical/actions)\n[![Coverage](https://codecov.io/gh/seandstewart/typical/branch/master/graph/badge.svg)](https://codecov.io/gh/seandstewart/typical)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![Netlify Status](https://api.netlify.com/api/v1/badges/982a0ced-bb7f-4391-87e8-1957071d2f66/deploy-status)](https://app.netlify.com/sites/typical-python/deploys)\n\n![How Typical](static/typical.png)\n\n## Introduction\n\nTypical is a library devoted to runtime analysis, inference,\nvalidation, and enforcement of Python types,\n[PEP 484](https://www.python.org/dev/peps/pep-0484/) Type Hints, and\ncustom user-defined data-types.\n\nTypical is fully compliant with the following Python Typing PEPs:\n\n- [PEP 484 -- Type Hints](https://www.python.org/dev/peps/pep-0484/)\n- [PEP 563 -- Postponed Evaluation of Annotations](https://www.python.org/dev/peps/pep-0563/)\n- [PEP 585 -- Type Hinting Generics In Standard Collections](https://www.python.org/dev/peps/pep-0585/)\n- [PEP 586 -- Literal Types](https://www.python.org/dev/peps/pep-0586/)\n- [PEP 589 -- TypedDict: Type Hints for Dictionaries with a Fixed Set of Keys](https://www.python.org/dev/peps/pep-0589/)\n- [PEP 604 -- Allow writing union types as X | Y](https://www.python.org/dev/peps/pep-0604/)\n\nIt provides a high-level Protocol API, Functional API, and Object API to suit most any\noccasion.\n\n## Getting Started\n\nInstallation is as simple as `pip install -U typical`.\n## Help\n\nThe latest documentation is hosted at\n[python-typical.org](https://python-typical.org/).\n\n> Starting with version 2.0, All documentation is hand-crafted\n> markdown & versioned documentation can be found at typical\'s\n> [Git Repo](https://github.com/seandstewart/typical/tree/master/docs).\n> (Versioned documentation is still in-the-works directly on our\n> domain.)\n\n## A Typical Use-Case\n\nThe decorator that started it all:\n\n### `typic.al(...)`\n\n```python\nimport typic\n\n\n@typic.al\ndef hard_math(a: int, b: int, *c: int) -> int:\n    return a + b + sum(c)\n\nhard_math(1, "3")\n#> 4\n\n\n@typic.al(strict=True)\ndef strict_math(a: int, b: int, *c: int) -> int:\n    return a + b + sum(c)\n\nstrict_math(1, 2, 3, "4")\n#> Traceback (most recent call last):\n#>  ...\n#> typic.constraints.error.ConstraintValueError: Given value <\'4\'> fails constraints: (type=int, nullable=False, coerce=False)\n  \n```\n\nTypical has both a high-level *Object API* and high-level\n*Functional API*. In general, any method registered to one API is also\navailable to the other.\n\n### The Protocol API\n\n```python\nimport dataclasses\nfrom typing import Iterable\n\nimport typic\n\n\n@typic.constrained(ge=1)\nclass ID(int):\n    ...\n\n\n@typic.constrained(max_length=280)\nclass Tweet(str):\n    ...\n\n\n@dataclasses.dataclass # or typing.TypedDict or typing.NamedTuple or annotated class...\nclass Tweeter:\n    id: ID\n    tweets: Iterable[Tweet]\n\n\njson = \'{"id":1,"tweets":["I don\\\'t understand Twitter"]}\'\nprotocol = typic.protocol(Tweeter)\n\nt = protocol.transmute(json)\nprint(t)\n#> Tweeter(id=1, tweets=["I don\'t understand Twitter"])\n\nprint(protocol.tojson(t))\n#> \'{"id":1,"tweets":["I don\\\'t understand Twitter"]}\'\n\nprotocol.validate({"id": 0, "tweets": []})\n#> Traceback (most recent call last):\n#>  ...\n#> typic.constraints.error.ConstraintValueError: Tweeter.id: value <0> fails constraints: (type=int, nullable=False, coerce=False, ge=1)\n```\n\n### The Functional API\n\n```python\nimport dataclasses\nfrom typing import Iterable\n\nimport typic\n\n\n@typic.constrained(ge=1)\nclass ID(int):\n    ...\n\n\n@typic.constrained(max_length=280)\nclass Tweet(str):\n    ...\n\n\n@dataclasses.dataclass # or typing.TypedDict or typing.NamedTuple or annotated class...\nclass Tweeter:\n    id: ID\n    tweets: Iterable[Tweet]\n\n\njson = \'{"id":1,"tweets":["I don\\\'t understand Twitter"]}\'\n\nt = typic.transmute(Tweeter, json)\nprint(t)\n#> Tweeter(id=1, tweets=["I don\'t understand Twitter"])\n\nprint(typic.tojson(t))\n#> \'{"id":1,"tweets":["I don\\\'t understand Twitter"]}\'\n\ntypic.validate(Tweeter, {"id": 0, "tweets": []})\n#> Traceback (most recent call last):\n#>  ...\n#> typic.constraints.error.ConstraintValueError: Tweeter.id: value <0> fails constraints: (type=int, nullable=False, coerce=False, ge=1)\n```\n\n### The Object API\n\n```python\nfrom typing import Iterable\n\nimport typic\n\n\n@typic.constrained(ge=1)\nclass ID(int):\n    ...\n\n\n@typic.constrained(max_length=280)\nclass Tweet(str):\n    ...\n\n\n@typic.klass\nclass Tweeter:\n    id: ID\n    tweets: Iterable[Tweet]\n    \n\njson = \'{"id":1,"tweets":["I don\\\'t understand Twitter"]}\'\nt = Tweeter.transmute(json)\n\nprint(t)\n#> Tweeter(id=1, tweets=["I don\'t understand Twitter"])\n\nprint(t.tojson())\n#> \'{"id":1,"tweets":["I don\\\'t understand Twitter"]}\'\n\nTweeter.validate({"id": 0, "tweets": []})\n#> Traceback (most recent call last):\n#>  ...\n#> typic.constraints.error.ConstraintValueError: Given value <0> fails constraints: (type=int, nullable=False, coerce=False, ge=1)\n```\n\n\n## Changelog\n\nSee our\n[Releases](https://github.com/seandstewart/typical/releases).\n',
    'author': 'Sean Stewart',
    'author_email': 'sean_stewart@me.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/seandstewart/typical',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
