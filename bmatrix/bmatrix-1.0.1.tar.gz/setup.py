# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bmatrix']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.1,<2.0.0', 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'bmatrix',
    'version': '1.0.1',
    'description': 'Package with tools for generating internal coordiantes and the corresponding B matrix for molecules and for periodic systems.',
    'long_description': '===============\nbmatrix package\n===============\n\nThis package contains tools for generating internal coordiantes and the\ncorresponding B matrix [1]_ for molecules as well as for periodic systems. It\nis a part of of the GADGET suite and if you use ``bmatrix`` in a scientific\npublication, please cite it as:\n\n  Bučko, T., Hafner, J., & Ángyán, J. G. (2005). Geometry optimization of\n  periodic systems using internal coordinates. *The Journal of Chemical Physics*,\n  122(12), 124508. `doi:10.1063/1.1864932 <http://doi.org/10.1063/1.1864932>`_\n\n\n.. [1] Wilson, E. B., Decius, J. C., & Cross, P. C. (1955). Molecular Vibrations: The\n   Theory of Infrared and Raman Vibrational Spectra. book, Dover Publications.\n',
    'author': 'Lukasz Mentel',
    'author_email': 'lmmentel@gmail.com',
    'maintainer': 'Lukasz Mentel',
    'maintainer_email': 'lmmentel@gmail.com',
    'url': 'https://github.com/lmmentel/bmatrix',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
