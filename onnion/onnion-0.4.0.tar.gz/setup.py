# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['onnion']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.0,<2.0.0', 'onnx>=1.9.0,<2.0.0']

entry_points = \
{'console_scripts': ['onnion = onnion.main:main']}

setup_kwargs = {
    'name': 'onnion',
    'version': '0.4.0',
    'description': 'onnx compiler',
    'long_description': '# onnion\n\n## Installation\n\n```\n$ pip3 install onnion\n```\n\n## Usage\n\n```\n$ onnion ssd-10-post.onnx -o ssd_post_model.py\n$ python\n>>> from ssd_post_model import init_graph\n>>> graph = init_graph()\n>>> inputs = ... # List[np.array]\n>>> outputs = graph.run(*inputs)\n```\n\nThe order of the inputs and the outputs in the `run` method corresponds to the order of the inputs and the outputs in the onnx graph.\n\nSee also [tutorial](https://github.com/Idein/onnion/tree/master#tutorial).\n\n## Development Guide\n\n```\n$ poetry install\n```\n',
    'author': 'Idein Inc.',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Idein/onnion/tree/master/compiler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
