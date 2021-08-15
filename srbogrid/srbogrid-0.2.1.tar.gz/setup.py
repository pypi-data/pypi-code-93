# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['srbogrid']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.3,<4.0.0', 'numpy>=1.21.1,<2.0.0', 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'srbogrid',
    'version': '0.2.1',
    'description': 'Package for calculating space-reduced bond-order grids for diatomics',
    'long_description': '# SRBOgrid - Space-Reduced Bond Order Grid\n\nThis module calculates the Space-Reduced Bond Order grids for optimal\nconfiguration space sampling of the potenial energy curves for diatomics.\n\nThe code is based on the work described in: Rampino, S. (2016). Configuration-Space Sampling in Potential Energy Surface Fitting: A Space-Reduced Bond-Order Grid Approach. The Journal of Physical Chemistry A, 120(27), 4683–4692. [doi: 10.1021/acs.jpca.5b10018](http://doi.org/10.1021/acs.jpca.5b10018)\n\n## Getting Started\n\nThese instructions will give you a copy of the project up and running on\nyour local machine for development and testing purposes. See deployment\nfor notes on deploying the project on a live system.\n\n### Installation\n\nBest way to install `srbogrid` is with `pip`:\n\n```bash\npip install srbogrid\n```\n\n### Example\n\n```python\nfrom srbogrid.srbo import SRBO\n```\n\nThe most straightforward way to compute the grid is to provide the parameters\n\n- `Re` :  eqilibrium bond distance in atomic units [bohr]\n- `De` : dissociation energy in atomic units [hartree]\n- `ke` : force constant in atomic units [hartree / bohr^2]\n\n#### Hydrogen molecule\n\nFor hydrogen molecule we can compute a SRBO grid with the following values:\n\n```python\nh2 = SRBO(Re=1.4034, De=0.1727, ke=0.3707)\nh2.grid\narray([0.63152744, 0.7632642 , 0.90460173, 1.05705019, 1.2225067 ,\n       1.4034    , 1.60290972, 1.82531189, 2.07654928, 2.36522877,\n       2.70449828, 3.1159375 , 3.63878276, 4.35671283, 5.50882366,\n       8.7400997 ])\n```\n\nBy default the grid will contain:\n\n- 5 points on the repulsive part of the potential energy curve (left from `Re`)\n- 10 points on the attractive part of the potential energy curve (right from `Re`)\n- `Re` point itself\n\nYou can get more information by printing the `summary`:\n\n```python\nprint(h2.summary())\n\nSystem info:\n\tRe        :   1.403400\n\tDe        :   0.172700\n\tke        :   0.370700\n\talpha     :   1.035977\n\nBoundaries:\n\trmin      :   0.631527\n\trmax      :   8.740100\n\tVfact     :   1.500000\n\tVthrs     :   0.001000\n\n\tBeta      :   0.515422\n\nGrid:\n\tnrep      :          5\n\tnatt      :         10\n\tnpoints   :         16\n\tf         :   2.000000\n\nGrid points:\n[0.63152744 0.7632642  0.90460173 1.05705019 1.2225067  1.4034\n 1.60290972 1.82531189 2.07654928 2.36522877 2.70449828 3.1159375\n 3.63878276 4.35671283 5.50882366 8.7400997 ]\n```\n\nYou can visualize the grid on a model Morse potential with:\n\n```python\nh2.plot_morse()\n```\n\n<p align="center">\n    <img src=".media/h2.png" alt="H2" width="800">\n</p>\n\n### More examples\n\nA short tutorial is available\n[here](http://nbviewer.jupyter.org/github/lmmentel/srbogrid/blob/master/notebooks/tutorial.ipynb) as a jupyter notebook.\n\n## License\n\nThis project is licensed under the [MIT](LICENSE.md)\nLicense - see the [LICENSE.md](LICENSE.md) file for\ndetails.\n',
    'author': 'Lukasz Mentel',
    'author_email': 'lmmentel@gmail.com',
    'maintainer': 'Lukasz Mentel',
    'maintainer_email': 'lmmentel@gmail.com',
    'url': 'https://github.com/lmmentel/srbogrid',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
