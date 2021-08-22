# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['powersddp', 'powersddp.core', 'powersddp.utils']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'cvxopt>=1.2.6,<2.0.0',
 'numpy>=1.21.1,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'plotly>=5.2.1,<6.0.0']

setup_kwargs = {
    'name': 'powersddp',
    'version': '0.0.1',
    'description': 'A Stochastic Dual Dynamic Programmimg library to solve economical dispach of power systems',
    'long_description': '[![PyPI version](https://badge.fury.io/py/powersddp.svg)](https://badge.fury.io/py/powersddp)\n\n# **Power** System **S**tochastic **D**ual **D**ynamic **P**rogramming\n\nThe main goal of this library is to provide support for studies regarding the optimal dispatch of power systems, majorly comprised of Thermoelectric and Hydroelectric Generators.\n\n> **Note 1** This is an under development library.\n\nA special thank should be given to professor **André Marcato**. This project does not intend to substitute the similar library `PySDDP`.\n\n> **Note 1** This project is being developed alongside the masters course: _Planejamento de Sistemas Elétricos_, as part of the masters program in Energy Systems at the [_Electrical Engineering Graduate Program_](https://www2.ufjf.br/ppee-en/) from the  _Universidade Federal de Juiz de Fora - Brazil_\n\n> **Note 2** The code will evolve alongside the video lectures provided by professor Marcato at: [Curso de Planejamento de Sistemas Elétricos](https://www.youtube.com/watch?v=a4D_mouXoUw&list=PLz7tpQ4EY_ne0gfWIqw6pJFrCglT6fjq7)\n\n## Installation\n\n```\npip install powersddp\n```\n\n## Example\n\nThere are two ways of initializing a `Power System`. Either by providing a `.yml` file, or by passing a dictionary as an initialization data. Both are depicted bellow:\n\n> **Note:** When using the file input method (`.yml` format) check the  [example](system.yml) of how to declare the parameters.\n\n\n### Initializing a `PowerSystem`\n```Python\nimport powersddp as psddp\n\nsystem = psddp.PowerSystem(path=\'system.yml\')\n\nprint("System Load: {}\\n"\n      "Number of HGUs: {}\\n"\n      "Number of TGUs: {}".format(system.data[\'load\'],\n                                  len(system.data[\'hydro-units\']),\n                                  len(system.data[\'thermal-units\'])))\n```\n\n```Python\nimport powersddp as psddp\n\ndata = {\'load\': [50, 50, 50],\n        \'discretizations\': 3,\n        \'stages\': 3,\n        \'scenarios\': 2,\n        \'outage_cost\': 500,\n        \'hydro-units\': [{\'name\': \'HU1\',\n                         \'v_max\': 100,\n                         \'v_min\': 20,\n                         \'prod\': 0.95,\n                         \'flow_max\': 60,\n                         \'inflow_scenarios\': [[23, 16], [19, 14], [15, 11]]}],\n        \'thermal-units\': [{\'name\': \'GT1\', \'capacity\': 15, \'cost\': 10},\n                          {\'name\': \'GT2\', \'capacity\': 10, \'cost\': 25}]}\n\nPowerSystem = psddp.PowerSystem(data=data)\n\nprint("System Load: {}\\n"\n      "Number of HGUs: {}\\n"\n      "Number of TGUs: {}".format(system.data[\'load\'],\n                                  len(system.data[\'hydro-units\']),\n                                  len(system.data[\'thermal-units\'])))\n```\n\n### Dispatching a `PowerSystem`\n\n#### **dispatch()** accepts the following arguments:\n\n- `verbose : bool, optional defaults to False`\n  - Displays the PDDE solution for every stage of the execution. Use with care, solutions of complex systems with too many stages and scenarios might overflow the console.\n\n- `plot : bool, optional, defaults to False`\n  - Displays a sequence of plots showing the future cost function for every stage of the execution. \n\n\n```Python\nimport powersddp as psddp\n\ndata = {\'load\': [50, 50, 50],\n        \'discretizations\': 3,\n        \'stages\': 3,\n        \'scenarios\': 2,\n        \'outage_cost\': 500,\n        \'hydro-units\': [{\'name\': \'HU1\',\n                         \'v_max\': 100,\n                         \'v_min\': 20,\n                         \'prod\': 0.95,\n                         \'flow_max\': 60,\n                         \'inflow_scenarios\': [[23, 16], [19, 14], [15, 11]]}],\n        \'thermal-units\': [{\'name\': \'GT1\', \'capacity\': 15, \'cost\': 10},\n                          {\'name\': \'GT2\', \'capacity\': 10, \'cost\': 25}]}\n\nPowerSystem = psddp.PowerSystem(data=data)\noperation = PowerSystem.dispatch()\n\nprint(operation)\n```\n<!-- <img src="https://render.githubusercontent.com/render/math?math=e^{i \\pi} = -1"> -->\n',
    'author': 'Ettore Aquino',
    'author_email': 'ettore@ettoreaquino.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ettoreaquino/powersddp.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
