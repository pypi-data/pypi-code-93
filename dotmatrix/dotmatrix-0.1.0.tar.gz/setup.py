# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dotmatrix']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dotmatrix',
    'version': '0.1.0',
    'description': 'A pixel matrix rendered using braille characters.',
    'long_description': '# dotmatrix\n_A dot matrix rendered using braille characters._\n\n## Description\n\nThis library provides class called `Matrix` which represents a dot matrix that can be rendered to a string of [Braille](https://en.wikipedia.org/wiki/Braille) characters. In addition the class also provides some usefull functions for drawing all kinds of things onto said matrix.\n## Install\n\nUse can install this library from [PyPI](https://pypi.org/project/dotmatrix/):\n\n```sh\npip install dotmatrix\n```\n\n### Example\n\n**Code**\n\n```python\nfrom dotmatrix import Matrix\n\nm = Matrix(64, 64)\n\nm.rectangle((0, 0), (63, 63))\nm.circle((31, 31), 31)\n\nprint(m.render())\n```\n\n**Output**\n\n```\n⡏⠉⠉⠉⠉⠉⠉⠉⢉⡩⠭⠛⠛⠉⠉⠉⠉⠉⠙⠛⠫⠭⣉⠉⠉⠉⠉⠉⠉⠉⠉⢹\n⡇⠀⠀⠀⠀⢀⡠⠊⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠢⣀⠀⠀⠀⠀⠀⢸\n⡇⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⢄⠀⠀⠀⢸\n⡇⠀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠢⡀⠀⢸\n⡇⡰⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⡀⢸\n⣧⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢣⢸\n⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣼\n⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿\n⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿\n⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⢹\n⡏⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡎⢸\n⡇⠘⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⠀⢸\n⡇⠀⠈⢢⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠊⠀⠀⢸\n⡇⠀⠀⠀⠑⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠔⠁⠀⠀⠀⢸\n⡇⠀⠀⠀⠀⠀⠈⠢⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠊⠀⠀⠀⠀⠀⠀⢸\n⣇⣀⣀⣀⣀⣀⣀⣀⣀⣈⣉⣒⣒⣤⣤⣤⣤⣤⣔⣒⣊⣉⣀⣀⣀⣀⣀⣀⣀⣀⣀⣸\n```\n\n## Drawing functions\n\nAs of now this library contains the following drawing functions:\n- `scatter` – Scatters some points.\n- `show` – Draws an object implementing the `Dotted` protocol.\n- `line` – Draws a line.\n- `chain` – Draws a chain of segments.\n- `polygon` – Draws a polygon.\n- `rectangle` – Draws an axis aligned rectangle. (from a simplified representation, i.e. from two opposing corners)\n- `cricle` – Draws a circle.\n- `ellipse` – Draws an axis aligned ellipse.\n- `plot` – Plots a series of XY-coordinates. (matplotlib.pyplot style)\n- `plotf` – Plots a function.\n- `curve` – Draws a [Bézier curve](https://en.wikipedia.org/wiki/B%C3%A9zier_curve).\n\nImplementing the `Dotted` protocol for any class comes down to adding a `__dots__` function to your class:\n\n```\ndef __dots__(self) -> Iterable[Tuple[int, int]]:\n    """Generate the pixel positions representing this object."""\n```\n\n⚠️&nbsp;&nbsp;_The origin or the coordinate system, i.e. `(0, 0)`, is at the top left corner!_\n\n\n## More examples\n\n### Bézier curves\n\n**Code**\n\n```python\nfrom dotmatrix import Matrix\n\nm = Matrix(64, 64)\n\nm.curve((0, 0), (63, 0), (0, 63), (63, 63))\nm.curve((0, 0), (0, 63), (63, 0), (63, 63))\nm.curve((63, 0), (0, 0), (63, 63), (0, 63))\nm.curve((63, 0), (63, 63), (0, 0), (0, 63))\n\nprint(m.render())\n```\n\n**Output**\n\n```\n⡏⠉⠉⠉⠉⠒⠒⠤⠤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠤⠤⠒⠒⠉⠉⠉⠉⢹\n⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠒⢄⠀⠀⠀⠀⠀⠀⡠⠒⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸\n⢣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⡄⠀⠀⢠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜\n⠘⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡆⢰⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠃\n⠀⢣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢱⡎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⠀\n⠀⠈⢢⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡔⠁⠀\n⠀⠀⠀⠑⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠊⠀⠀⠀\n⠀⠀⠀⠀⠀⠉⠢⠤⢄⣀⣀⣀⣀⣀⣀⣸⣇⣀⣀⣀⣀⣀⣀⡠⠤⠔⠉⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⣀⠤⠒⠒⠉⠉⠉⠉⠉⠉⢹⡏⠉⠉⠉⠉⠉⠉⠒⠒⠤⣀⠀⠀⠀⠀⠀\n⠀⠀⠀⡠⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⢄⠀⠀⠀\n⠀⢀⠎⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⡀⠀\n⠀⡜⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⢣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢣⠀\n⢰⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠃⠘⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡆\n⡜⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠃⠀⠀⠘⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢣\n⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡠⠊⠀⠀⠀⠀⠀⠀⠑⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸\n⣇⣀⣀⣀⣀⠤⠤⠔⠒⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠒⠢⠤⠤⣀⣀⣀⣀⣸\n```\n\n### Function plotting\n\n**Code**\n\n```python\nfrom dotmatrix import Matrix\n\nm = Matrix(64, 64)\n\nm.plotf(\n    lambda x: 0.005 * x ** 3,\n    range(-31, 31),\n    origin=(31,31),\n)\n\nprint(m.render())\n```\n\n**Output**\n\n```\n⠀⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⢱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠈⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠸⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠢⢄⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠢⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡀⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢣⠀⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢣⠀⠀⠀⠀⠀⠀⠀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡀⠀⠀⠀⠀⠀⠀\n```\n',
    'author': 'Tim Fischer',
    'author_email': 'me@timfi.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/timfi/dotmatrix',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
