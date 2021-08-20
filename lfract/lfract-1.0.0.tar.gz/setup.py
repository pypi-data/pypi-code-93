# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['src']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=4.0']

entry_points = \
{'console_scripts': ['lfract = src.lfract:main']}

setup_kwargs = {
    'name': 'lfract',
    'version': '1.0.0',
    'description': 'An open-source CLI software for generating fractal images using the L-System.',
    'long_description': '\n# L-System Fractal Generator\n\nAn open-source CLI software for generating fractal images using the L-System.\n\n## Features\n\n- Rewrite and draw a 2D deterministic context-free L-System. (D0L)\n- Support the following turtle commands:\n\n|  Command  | Description | \n| :-------- | :----------- |\n| F         | Draw a line forward *d* pixels in the current heading|\n| f         | Move forward *d* pixels in the current heading without drawing a line|\n| +         | Turn right by *δ* degrees |\n| -         | Turn left by *δ* degrees |\n| [         | Push the current turtle\'s state into a stack |\n| ]         | Pop a turtle\'s state out of the stack |\n\n- Support saving and previewing the output image\n- Support changing the drawing line\'s width\n\n## Background\n\n\nL-System (Lindenmayer System) is a string rewriting system that uses an iterative process. An L-System starts with ***an axiom***, an initial string, that will be rewritten following a set of ***production rules*** which contains pairs of ***predecessors*** and ***successors***. For each iteration, each symbol or character will be replaced with its corresponding successor. Any symbols without a production rule will be replaced by themselves. For example,\n\n> **Axiom:** N  \n> **Production Rules:**\n> |Predecessor|Successor|\n> |:---|:---|\n> |N|MNO|\n> |O|#|\n>\n> **Iteration 0:** N  \n> **Iteration 1:** MNO  \n> **Iteration 2:** MMNO#  \n> **Iteration 3:** MMMNO##  \n\nFor illustration, ```lfract``` reserves some characters for controlling a drawing pen called ***a turtle***. The turtle keeps track of its position and heading throughout the evaluation process. After some finite number of iterations, the resulting string will be evaluated and an image will be drawn. (Supported turtle commands are listed in the previous section)  \n\nThe current version of ```lfract``` supports only the deterministic and context-free version of the L-System. That is each rule has a probability of being applied of 1 and the location of each symbol in a string relative to other symbols doesn\'t matter.\n\n## Installation\n\nThis software is available to download on The Python Package Index (PyPI) and can be installed through ```pip```.  \n\nStart by making sure that ```pip``` is installed and up-to-date\n> ```python -m pip install --upgrade pip```\n\nRun the following command on your terminal\n\n> ```pip install lfract```\n\n## Usage\n\nInvokes the program using ```lfract```. There are seven optional arguments as follows:\n\n| Option |Description|\n| :--- | :----- |\n| -x, --axiom  | Initial string or axiom, required |\n| -r, --rules  | Production rules. Uses "->" to seperate predecessor from successor, optional |\n| -a, --angle  | Turning angle, *δ* (degrees), default = 90 |\n| -d, --dist   | Distance, *d* (pixels), default = 100 |\n| -n, --iters  | Number of iterations, default = 0 |\n| -o, --output | Output path. If specified, the image will be saved to the given path, optional |\n| -w, --width  | Width of the drawing pen (pixels), default = 1 |\n\nThe user must provide at least an axiom or the initial string to the L-System. All predecessors in the set of production rules must be unique. If there are duplicates, ```lfract``` will use the latest rule.\n\nFor the full usage description of ```lfract```, type:\n> ```lfract --help```\n\n## Examples\n\n1. Hilbert curve by Prusinkiewicz and Hanan [1]\n   > ```lfract -x X -r X->-YF+XFX+FY- Y->+XF-YFY-FX+ -a 90 -d 50 -n 5 -w 5```\n\n![hilbert](/images/hilbert.jpeg)\n\n2. Hexagonal tiling by Prusunkiewicz and Hanan [1]\n   > ```lfract -x X -r X->[-F+F[Y]+F][+F-F[X]-F] Y->[-F+F[Y]+F][+F-F-F] -a 60 -d 50 -n 10 -w 4```\n\n![hex](/images/hex.jpeg)\n\n3. A fractal by Surasith Boonaneksap\n   > ```lfract -x A -r A->fB+AF+Fff+Bf B->Bf-FffF-FfA-Afff -a 120 -n 7 -d 50 -w 5```\n\n![ex1](/images/ex1.jpeg)\n\n## Notes\n\n  - ```lfract``` adopts the L-System formal definition from [1]. It also follows the terminologies used in [1][2][3].\n  - Symbols in the L-System can be any Unicode characters.\n  - Currently not support:\n    - Stochastic L-System\n    - Context-sensitive L-System\n    - Parametric L-System\n\n## Dependency\n\nPillow 4.0.0 (Depending on the Python\'s version, a more recent version may be required. Check [Pillow\'s documentation](https://pillow.readthedocs.io/en/stable/installation.html#python-support))\n\n## License\n\nMIT\n\n## References\n\n[1]: Prunsinkiewicz, Przemyslaw and Hanan, James; "Lecture Notes in Biomathematics: Lindenmayer Systems, Fractals, and Plants" [link](http://algorithmicbotany.org/papers/lsfp.pdf)  \n[2]: Wikipedia; "L-system" [link](https://en.wikipedia.org/wiki/L-system)  \n[3]: Santel, Jordan; "L-systems" [link](https://jsantell.com/l-systems/)  ',
    'author': 'Surasith Boonaneksap',
    'author_email': 'surasith.boo@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SurasithO/lfract',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
