# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dsplot', 'dsplot.graph', 'dsplot.matrix', 'dsplot.tree']

package_data = \
{'': ['*']}

install_requires = \
['pygraphviz>=1.7,<2.0']

setup_kwargs = {
    'name': 'dsplot',
    'version': '0.5.0',
    'description': 'Visualize Tree, Graph, and Matrix data structures with ease.',
    'long_description': '# Data Structure Plot (DSPlot)\n[![Build Status](https://travis-ci.com/billtrn/dsplot.svg?branch=master)](https://travis-ci.com/billtrn/dsplot)\n[![Coverage Status](https://coveralls.io/repos/github/billtrn/dsplot/badge.svg?branch=master)](https://coveralls.io/github/billtrn/dsplot?branch=master)\n[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/billtrn/dsplot/blob/master/LICENSE)\n\nDSPlot is a tool to simply visualize tree and graph data structures by serving as a Pythonic interface to the [Graphviz](https://graphviz.org/) layout.\nDSPlot allows you to easily draw trees, graphs (both directed and undirected), and matrices by passing data in primitive form and directly output an image.\n\n## ⬇ Installation\n\n#### 0. Prerequisites\n- Python 3.7 or later\n- `pip`\n- `virtualenv`\n\n#### 1. Install Graphviz\n- MacOS:\n```\nbrew install graphviz\n```\n- Linux:\n```\napt-get install graphviz\n```\n- Other OS(s): https://graphviz.org/download/\n\n#### 2. Install package\n```\n$ pip install dsplot\n```\n\n## 🤟 Usage\n- Binary Tree:\n```python\nfrom dsplot.tree import BinaryTree\n\ntree = BinaryTree(nodes=[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1])\ntree.plot()\n```\n![tree](https://github.com/billtrn/dsplot/blob/master/img/tree.png?raw=true)\n\n- Graph:\n```python\nfrom dsplot.graph import Graph\n\ngraph = Graph(\n    {0: [1, 4, 5], 1: [3, 4], 2: [1], 3: [2, 4], 4: [], 5: []}, directed=True\n)\ngraph.plot()\n```\n![directed](https://github.com/billtrn/dsplot/blob/master/img/directed.png?raw=true)\n```python\nfrom dsplot.graph import Graph\n\ngraph = Graph(\n    {1: [2, 4], 2: [1, 3], 3: [2, 4, 5], 4: [1, 3], 5: [3, 6, 7], 6: [5], 7: [5]}, directed=False\n)\ngraph.plot()\n```\n![undirected](https://github.com/billtrn/dsplot/blob/master/img/undirected.png?raw=true)\n\n- Matrix:\n```python\nfrom dsplot.matrix import Matrix\n\nmatrix = Matrix([[1, 2, 3], [4, 5, 6], [1, 2, 6]])\nmatrix.plot()\n```\n![matrix](https://github.com/billtrn/dsplot/blob/master/img/matrix.png?raw=true)\n\n## 🎁 Additional features\n### 1. Tree traversals:\n```python\nfrom dsplot.tree import BinaryTree\n\ntree = BinaryTree(nodes=[5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1])\n\nprint(tree.preorder())\n# [5, 4, 11, 7, 2, 8, 13, 4, 5, 1]\n\nprint(tree.inorder())\n# [7, 11, 2, 4, 5, 13, 8, 5, 4, 1]\n\nprint(tree.postorder())\n# [7, 2, 11, 4, 13, 5, 1, 4, 8, 5]\n```\n### 2. Graph traversals:\n```python\nfrom dsplot.graph import Graph\n\ngraph = Graph(\n    {0: [1, 4, 5], 1: [3, 4], 2: [1], 3: [2, 4], 4: [], 5: []}, directed=True\n)\n\nprint(graph.bfs())\n# [0, 1, 4, 5, 3, 2]\n\nprint(graph.dfs())\n# [0, 1, 3, 2, 4, 5]\n```\n## 📄 License\n[MIT](./LICENSE)\n',
    'author': 'Bill',
    'author_email': 'trantriducs@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
