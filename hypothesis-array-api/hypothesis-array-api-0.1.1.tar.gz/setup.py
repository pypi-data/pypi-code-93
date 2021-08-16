# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['hypothesis_array']
install_requires = \
['hypothesis>=6.14.1,<7.0.0']

extras_require = \
{'docs': ['sphinx>=3,<4']}

setup_kwargs = {
    'name': 'hypothesis-array-api',
    'version': '0.1.1',
    'description': 'Hypothesis strategies for Array API libraries',
    'long_description': '# Hypothesis strategies for Array API libraries\n\n**Note:** `hypothesis-array-api` uses private APIs from Hypothesis\nand so should be considered unstable.\n\n## Install\n\nYou can get the strategies from PyPI.\n\n```bash\npip install hypothesis-array-api\n```\n\nTo install from source,\n[get Poetry](https://python-poetry.org/docs/#installation)\nand then `poetry install` inside the repository.\nUsing `poetry shell` is a good idea for development,\nwhere you can use `pytest` to run the full test suite\n(note there a lot of expected warnings I need to declutter.)\n\n## Quickstart\n\n```python\nfrom numpy import array_api as xp\n\nfrom hypothesis import given\nfrom hypothesis_array import get_strategies_namespace\n\nxps = get_strategies_namespace(xp)\n\n@given(xps.arrays(dtype=xps.scalar_strategies(), shape=xps.array_shapes()))\ndef your_test(array):\n    ...\n```\n\n## Contributors\n\n[@honno](https://github.com/honno/) created these strategies\nwith input from\n[@mattip](https://github.com/mattip),\n[@asmeurer](https://github.com/asmeurer),\n[@rgommers](https://github.com/rgommers)\nand other great folk from\n[@Quansight-Labs](https://github.com/Quansight-Labs).\n\nInspiration was taken from the\n[NumPy strategies](https://hypothesis.readthedocs.io/en/latest/numpy.html#numpy)\nthat Hypothesis ships with at `hypothesis.extra.numpy`.\nThanks to the Hypothesis contributors who helped shape it, including:\n[@Zac-HD](https://github.com/Zac-HD),\n[@rsokl](https://github.com/rsokl),\n[@DRMacIver](https://github.com/DRMacIver),\n[@takluyver](https://github.com/takluyver),\n[@rdturnermtl](https://github.com/rdturnermtl),\n[@kprzybyla](https://github.com/kprzybyla),\n[@sobolevn](https://github.com/sobolevn),\n[@kir0ul](https://github.com/kir0ul),\n[@lmount](https://github.com/lmount),\n[@jdufresne](https://github.com/jdufresne),\n[@gsnsw-felixs](https://github.com/gsnsw-felixs) and\n[@alexwlchan](https://github.com/alexwlchan).\n',
    'author': 'Matthew Barber',
    'author_email': 'quitesimplymatt@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/honno/hypothesis-array-api',
    'py_modules': modules,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
