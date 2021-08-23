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
    'version': '0.3.0',
    'description': 'A Python interface to the Exact integer linear programming solver',
    'long_description': '# Exact\n\n[Exact](https://gitlab.com/JoD/exact) solves decision and optimization problems formulated as binary linear programs, also known as 0-1 integer linear programs or pseudo-Boolean formulas.\n\nExact is a fork of [RoundingSat](https://gitlab.com/miao_research/roundingsat) and improves upon its predecessor in reliability, performance and ease-of-use.\nThe name "Exact" reflects that the answers are fully sound, as approximate and floating-point calculations only occur in heuristic parts of the algorithm.\nAs such, Exact can soundly be used for verification and theorem proving, where its envisioned ability to emit machine-checkable certificates of optimality and unsatisfiability should prove useful.\n\n## Features\n\n- Native conflict analysis over binary linear constraints, constructing full-blown cutting planes proofs.\n- Highly efficient watched propagation routines.\n- Seamless use of arbitrary precision arithmetic.\n- Hybrid linear (top-down) and core-guided (bottom-up) optimization.\n- Optional integration with the SoPlex LP solver.\n- Compiles on macOS.\n- Python interface with assumption solving. Published as a [PyPI package](https://pypi.org/project/exact). (supporting only Linux for now)\n- Under development: generation of certificates of optimality and unsatisfiability that can be automatically verified by [VeriPB](https://github.com/StephanGocht/VeriPB).\n\n## Usage\n\n**TODO: explain how to use this Python package**\n\n## Build\n\nafter moving the .so and the headers to the folder `exact`, run\n\n```\n$ poetry build\n$ poetry publish\n```\n\n## Citations\n\nOrigin paper with a focus on cutting planes conflict analysis:  \n**[EN18]** J. Elffers, J. Nordström. Divide and Conquer: Towards Faster Pseudo-Boolean Solving. *IJCAI 2018*\n\nIntegration with SoPlex:  \n**[DGN20]** J. Devriendt, A. Gleixner, J. Nordström. Learn to Relax: Integrating 0-1 Integer Linear Programming with Pseudo-Boolean Conflict-Driven Search. *CPAIOR 2020 / Constraints journal*\n\nWatched propagation:  \n**[D20]** J. Devriendt. Watched Propagation for 0-1 Integer Linear Constraints. *CP 2020*\n\nCore-guided optimization:  \n**[DGDNS21]** J. Devriendt, S. Gocht, E. Demirović, J. Nordström, P. J. Stuckey. Cutting to the Core of Pseudo-Boolean Optimization: Combining Core-Guided Search with Cutting Planes Reasoning. *AAAI 2021*\n',
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
