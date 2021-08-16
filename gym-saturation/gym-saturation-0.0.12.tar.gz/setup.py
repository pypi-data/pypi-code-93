# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gym_saturation',
 'gym_saturation.envs',
 'gym_saturation.logic_ops',
 'gym_saturation.parsing']

package_data = \
{'': ['*'],
 'gym_saturation': ['resources/*',
                    'resources/TPTP-mock/Axioms/*',
                    'resources/TPTP-mock/Problems/TST/TST001-1.p',
                    'resources/TPTP-mock/Problems/TST/TST001-1.p',
                    'resources/TPTP-mock/Problems/TST/TST002-1.p',
                    'resources/TPTP-mock/Problems/TST/TST002-1.p']}

install_requires = \
['gym', 'lark-parser']

extras_require = \
{':python_version < "3.7"': ['dataclasses'],
 ':python_version < "3.9" and python_version >= "3.7"': ['importlib_resources']}

setup_kwargs = {
    'name': 'gym-saturation',
    'version': '0.0.12',
    'description': 'An OpenAI Gym environment for saturation provers',
    'long_description': '[![PyPI version](https://badge.fury.io/py/gym-saturation.svg)](https://badge.fury.io/py/gym-saturation) [![CircleCI](https://circleci.com/gh/inpefess/gym-saturation.svg?style=svg)](https://circleci.com/gh/inpefess/gym-saturation) [![Documentation Status](https://readthedocs.org/projects/gym-saturation/badge/?version=latest)](https://gym-saturation.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/inpefess/gym-saturation/branch/master/graph/badge.svg)](https://codecov.io/gh/inpefess/gym-saturation)\n\nDocumentation is hosted [here](https://gym-saturation.readthedocs.io/en/latest).\n',
    'author': 'Boris Shminke',
    'author_email': 'boris@shminke.ml',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/inpefess/gym-saturation',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
