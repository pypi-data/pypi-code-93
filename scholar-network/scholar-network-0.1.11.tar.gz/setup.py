# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['scholar_network']

package_data = \
{'': ['*']}

install_requires = \
['selenium>=3.141.0,<4.0.0']

setup_kwargs = {
    'name': 'scholar-network',
    'version': '0.1.11',
    'description': 'Graph Network Analysis for scraping Google Scholar authors.',
    'long_description': "# Welcome to Scholar Network\n\nThis package is intended for people wanting to scrape Google Scholar\nto build graph networks of Google Scholar authors and identify network\nconnections as opportunities for collaboration.\n\n## Documentation\n\nAPI Reference Documentation available [here](https://uk-ipop.github.io/scholar-network/)\n\n## Features\n\n1. Selenium based web scraping\n2. Poetry based dependency management\n3. Basic Graph algorithms and metrics\n\n## ToDo:\n\n- Write tests\n\n## Usage\n\nTo get started you can clone the repo and activate the poetry environment.\n\n```\ngit clone https://github.com/UK-IPOP/scholar-network.git\ncd scholar-network\npoetry install --no-dev\npoetry shell\n```\n\nThen start hacking! 😃\n\n### Examples\n\n_You must know each author's Google Scholar ID for this package to work._\n\nScraping one author (my wife, for example):\n```python\n>>>import scholar_network as sn\n>>>sn.scrape_single_author(scholar_id='ZmwzVQUAAAAJ', scholar_name='Michelle Duong')\n```\nThe data for the author will then be in your `data/scraped.json` file.\n\nTo create a graph from this new data is easy:\n```python\n>>>g = sn.build_graph()\n```\n\nThen, to see the most common five (5) connections:\n```python\n>>>g.edge_rank(limit=5)\nOut[4]:\n[(('David Burgess', 'Donna Burgess'), 64),\n (('Ashley Martinez', 'Daniela Moga'), 64),\n (('Daniela Moga', 'Erin Abner'), 62),\n (('Donna Burgess', 'Katie Wallace'), 62),\n (('Chang-Guo Zhan', 'Fang Zheng'), 60)]\n```\n",
    'author': 'Nick Anthony',
    'author_email': 'nanthony007@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
