# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slumba']

package_data = \
{'': ['*']}

install_requires = \
['llvmlite==0.36.0', 'numba==0.53.1']

setup_kwargs = {
    'name': 'slumba',
    'version': '3.1.0',
    'description': 'JITted SQLite user-defined functions and aggregates',
    'long_description': '# Put some Numba in your SQLite\n\n## Fair Warning\n\nThis library does unsafe things like pass around function pointer addresses\nas integers.  **Use at your own risk**.\n\nIf you\'re unfamiliar with why passing function pointers\' addresses around as\nintegers might be unsafe, then you shouldn\'t use this library.\n\n## Requirements\n\n* Python `>=3.7`\n* `numba`\n\nUse `nix-shell` from the repository to avoid dependency hell.\n\n## Installation\n\n* `poetry install`\n\n## Examples\n\n### Scalar Functions\n\nThese are almost the same as decorating a Python function with `numba.jit`.\n\n```python\nfrom typing import Optional\n\nfrom slumba import sqlite_udf\n\n\n@sqlite_udf\ndef add_one(x: Optional[int]) -> Optional[int]:\n    """Add one to `x` if `x` is not NULL."""\n\n    if x is not None:\n        return x + 1\n    return None\n```\n\n\n### Aggregate Functions\n\nThese follow the API of the Python standard library\'s\n`sqlite3.Connection.create_aggregate` method. The difference with slumba\naggregates is that they require two decorators: `numba.experimental.jit_class` and\n`slumba.sqlite_udaf`. Let\'s define the `avg` (arithmetic mean) function for\n64-bit floating point numbers.\n\n```python\nfrom typing import Optional\n\nfrom numba.experimental import jitclass\n\nfrom slumba import sqlite_udaf\n\n\n@sqlite_udaf\n@jitclass\nclass Avg:\n    total: float\n    count: int\n\n    def __init__(self):\n        self.total = 0.0\n        self.count = 0\n\n    def step(self, value: Optional[float]) -> None:\n        if value is not None:\n            self.total += value\n            self.count += 1\n\n    def finalize(self) -> Optional[float]:\n        if not self.count:\n            return None\n        return self.total / self.count\n```\n\n### Window Functions\n\nYou can also define window functions for use with SQLite\'s `OVER` construct:\n\n```python\nfrom typing import Optional\n\nfrom numba.experimental import jitclass\n\nfrom slumba import sqlite_udaf\n\n\n@sqlite_udaf\n@jitclass\nclass WinAvg:  # pragma: no cover\n    total: float\n    count: int\n\n    def __init__(self) -> None:\n        self.total = 0.0\n        self.count = 0\n\n    def step(self, value: Optional[float]) -> None:\n        if value is not None:\n            self.total += value\n            self.count += 1\n\n    def finalize(self) -> Optional[float]:\n        count = self.count\n        if count:\n            return self.total / count\n        return None\n\n    def value(self) -> Optional[float]:\n        return self.finalize()\n\n    def inverse(self, value: Optional[float]) -> None:\n        if value is not None:\n            self.total -= value\n            self.count -= 1\n```\n\n#### Calling your aggregate function\n\nSimilar to scalar functions, we register the function with a `sqlite3.Connection` object:\n\n```python\n>>> import sqlite3\n>>> from slumba import create_aggregate, create_function\n>>> con = sqlite3.connect(":memory:")\n>>> create_function(con, "add_one", 1, add_one)\n>>> con.execute("SELECT add_one(1)").fetchall()\n[(2,)]\n```\n',
    'author': 'Phillip Cloud',
    'author_email': '417981+cpcloud@users.noreply.github.com',
    'maintainer': 'Phillip Cloud',
    'maintainer_email': '417981+cpcloud@users.noreply.github.com',
    'url': 'https://github.com/cpcloud/slumba',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.8,<3.10',
}


setup(**setup_kwargs)
