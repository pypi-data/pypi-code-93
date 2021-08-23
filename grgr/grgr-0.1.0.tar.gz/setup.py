# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['grgr', 'grgr.dev', 'grgr.ggplot2']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0', 'pandas>=1.3.2,<2.0.0', 'rpy2>=3.4.5,<4.0.0']

setup_kwargs = {
    'name': 'grgr',
    'version': '0.1.0',
    'description': '`grgr` is a wrapper library for using `ggplot2` from `python`.',
    'long_description': "# grgr\n`grgr` is a library for using `ggplot2` from `python`.  \n\n`grgr` can create figures in `python` using grammar similar to `ggplot2`. `python` does not create the figure itself, but generates a code that can be executed in `R`, and executes it in R to create the figure. In other words, `grgr` is an interface from `python` to `R`'s `ggplot2`. Therefore, this library directly depends on `R` and `ggplot2`.\n\n# Quickstart\nYou can install `grgr` through `pip` by running `pip install grgr`. In order to use `grgr`, you need to have `R` and `ggplot2` installed. Please make sure that these are installed beforehand. Once the installation is complete, you can draw a figure in `python` with the grammer same as `ggplot2`. A basic usage example can be found in `example/basic.py`.\n",
    'author': '7cm-diameter',
    'author_email': 'from.this.ridiculous.loop@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/7cm-diameter/grgr/wiki',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
