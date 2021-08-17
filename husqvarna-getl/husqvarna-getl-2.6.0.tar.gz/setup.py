# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['getl',
 'getl.blocks',
 'getl.blocks.custom',
 'getl.blocks.load',
 'getl.blocks.transform',
 'getl.blocks.transform.add_column',
 'getl.blocks.write',
 'getl.common',
 'getl.fileregistry']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.13.24,<2.0.0',
 'oyaml>=0.9,<1.1',
 'pyspark>=2.4.4,<3.1',
 'typeguard>=2.10.0,<3.0.0']

extras_require = \
{':extra == "mysql"': ['mysql-connector-python>=8.0.23,<9.0.0'],
 'postgres': ['psycopg2-binary>=2.8,<3.0']}

entry_points = \
{'mkdocs.plugins': ['LiftBlock = mkdocs_plugins:LiftBlock',
                    'RootFiles = mkdocs_plugins:RootFiles']}

setup_kwargs = {
    'name': 'husqvarna-getl',
    'version': '2.6.0',
    'description': "An elegant way to ETL'ing",
    'long_description': "GETL\n====\n\n[![Build Status](https://dev.azure.com/husqvarna-ailab/GETL/_apis/build/status/husqvarnagroup.GETL?branchName=master)](https://dev.azure.com/husqvarna-ailab/GETL/_build?definitionId=1&branchName=master)\n[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=GETL&metric=alert_status)](https://sonarcloud.io/dashboard?id=GETL)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\nAn elegant way to ETL'ing.\n\n- View the [GETL documentation](https://getl.readthedocs.io)\n\n\nInstallation\n------------\n\nInstall GETL by running:\n\n```sh\npip install husqvarna-getl\n```\n\nUpcoming features\n--------\n\n- Lift definition validation\n\n\nContribute\n----------\n\n- Issue Tracker: https://github.com/husqvarnagroup/GETL/issues\n- Source Code: https://github.com/husqvarnagroup/GETL\n\nSupport\n-------\n\nIf you are having issues, please create an issue on our [github](https://github.com/husqvarnagroup/GETL/issues).\n\nLicense\n-------\n\nMIT License\n",
    'author': 'Linus Wallin',
    'author_email': 'linus.wallin@husqvarnagroup.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/husqvarnagroup/GETL/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
