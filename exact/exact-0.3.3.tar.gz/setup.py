# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exact']

package_data = \
{'': ['*'],
 'exact': ['headers/*',
           'headers/constraints/*',
           'headers/datastructures/*',
           'headers/propagation/*',
           'headers/used_licenses/*']}

install_requires = \
['cppyy>=2.1.0,<3.0.0']

setup_kwargs = {
    'name': 'exact',
    'version': '0.3.3',
    'description': 'A Python interface to the Exact integer linear programming solver',
    'long_description': '# Exact\n\n[Exact](https://gitlab.com/JoD/exact) solves decision and optimization problems formulated as integer linear programs. Under the hood, it converts integer variables to binary (0-1) variables and applies highly efficient propagation routines and strong pseudo-Boolean conflict analysis.\n\nExact is a fork of [RoundingSat](https://gitlab.com/miao_research/roundingsat) and improves upon its predecessor in reliability, performance and ease-of-use.\nThe name "Exact" reflects that the answers are fully sound, as approximate and floating-point calculations only occur in heuristic parts of the algorithm.\nAs such, Exact can soundly be used for verification and theorem proving, where its envisioned ability to emit machine-checkable certificates of optimality and unsatisfiability should prove useful.\n\n## Features\n\n- **Native conflict analysis** over binary linear constraints, constructing full-blown cutting planes proofs.\n- Highly efficient **watched propagation** routines.\n- Seamless use of **arbitrary precision** arithmetic when needed.\n- Hybrid linear (top-down) and **core-guided** (bottom-up) optimization.\n- Optional integration with the **SoPlex LP solver**.\n- Compiles on **macOS**.\n- **Python** interface with assumption solving and reuse of solver state.\n- Under development: generation of **certificates** of optimality and unsatisfiability that can be automatically verified by [VeriPB](https://github.com/StephanGocht/VeriPB).\n\n## Python usage\n\nEither compile a shared library locally or use the published [PyPI package](https://pypi.org/project/exact) (Linux only for now) via the `pip` or `poetry` package managers.\n\nThe header file [`Exact.hpp`](https://gitlab.com/JoD/exact/-/blob/master/src/Exact.hpp) contains the C++ methods exposed to Python via [cppyy](https://cppyy.readthedocs.io/en/latest) as well as their description. This is probably the place to start to learn about Exact\'s Python usage.\n\nNext, [`python/examples`](https://gitlab.com/JoD/exact/-/blob/master/python/examples) contains two commented instructive examples.\n- [`python/examples/knapsack_classic.py`](https://gitlab.com/JoD/exact/-/blob/master/python/examples/knapsack_classic.py) showcases how to solve an integer classic knapsack problem with Exact\'s Python interface.\n- [`python/examples/knapsack_implied.py`](https://gitlab.com/JoD/exact/-/blob/master/python/examples/knapsack_implied.py), elaborates on the first and showcases how to find the variable assignments implied by optimality, i.e., the variable assignments shared by all optimal solutions. A combination of the mechanics of assumption and solution invalidation allow to reuse the existing solver state (containing learned constraints) for optimal performance.\n\n## File-based usage\n\nExact takes as input an integer linear program and outputs a(n optimal) solution or reports that none exists.\nEither pipe the program\n\n    cat test/instances/opb/opt/stein15.opb | build/Exact\n\nor pass the file as a parameter\n\n    build/Exact test/instances/opb/opt/stein15.opb\n\nUse the flag `--help` to display a list of runtime parameters.\n\nExact supports five input formats (described in more detail in [`InputFormats.md`](https://gitlab.com/JoD/exact/-/blob/master/InputFormats.md)):\n- `.opb` pseudo-Boolean PBO (only linear objective and constraints)\n- `.cnf` DIMACS Conjunctive Normal Form (CNF)\n- `.wcnf` Weighted Conjunctive Normal Form (WCNF)\n- `.mps` Mathematical Programming System (MPS) via the optional CoinUtils library\n- `.lp` Linear Program (LP) via the optional CoinUtils library\n\nBy default, Exact decides on the format based on the filename extension, but this can be overridden with the `--format` option.\n\n## Compilation\n\nIn the root directory of Exact:\n\n    cd build\n    cmake -DCMAKE_BUILD_TYPE=Release ..\n    make\n\nFor a debug build:\n\n    cd build_debug\n    cmake -DCMAKE_BUILD_TYPE=Debug ..\n    make\n\nFor more builds, similar build directories can be created.\n\nFor installing system-wide or to the `CMAKE_INSTALL_PREFIX` root, use `make install`.\n\n## Dependencies\n\n- C++17 (i.e., a reasonably recent C++ compiler)\n- [Boost](https://www.boost.org) library.\n  On a Debian/Ubuntu system, install with `sudo apt install libboost-all-dev`.\n- Optionally: [CoinUtils](https://github.com/coin-or/CoinUtils) library to parse MPS and LP file formats.\n  On a Debian/Ubuntu system, install with `sudo apt install coinor-libcoinutils-dev`.\n- Optionally: [SoPlex](https://soplex.zib.de) LP solver (see below)\n\n## SoPlex\n\nExact supports an integration with the LP solver [SoPlex](https://soplex.zib.de) to improve its search routine.\nFor this, first [download](https://soplex.zib.de/download.php?fname=soplex-5.0.2.tgz) SoPlex 5.0.2 and place the downloaded file in the root directory of Exact.\nNext, follow the above build process, but configure with the cmake option `-Dsoplex=ON`:\n\n    cd build\n    cmake -DCMAKE_BUILD_TYPE=Release -Dsoplex=ON ..\n    make\n\nThe location of the SoPlex package can be configured with the cmake option `-Dsoplex_pkg=<location>`.\n\n## Citations\n\nOrigin paper with a focus on cutting planes conflict analysis:  \n**[EN18]** J. Elffers, J. Nordström. Divide and Conquer: Towards Faster Pseudo-Boolean Solving. *IJCAI 2018*\n\nIntegration with SoPlex:  \n**[DGN20]** J. Devriendt, A. Gleixner, J. Nordström. Learn to Relax: Integrating 0-1 Integer Linear Programming with Pseudo-Boolean Conflict-Driven Search. *CPAIOR 2020 / Constraints journal*\n\nWatched propagation:  \n**[D20]** J. Devriendt. Watched Propagation for 0-1 Integer Linear Constraints. *CP 2020*\n\nCore-guided optimization:  \n**[DGDNS21]** J. Devriendt, S. Gocht, E. Demirović, J. Nordström, P. J. Stuckey. Cutting to the Core of Pseudo-Boolean Optimization: Combining Core-Guided Search with Cutting Planes Reasoning. *AAAI 2021*\n',
    'author': 'Jo Devriendt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/JoD/exact',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
