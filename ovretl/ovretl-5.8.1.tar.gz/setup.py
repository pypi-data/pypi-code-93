# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ovretl',
 'ovretl.billings_utils',
 'ovretl.billings_utils.tests',
 'ovretl.containers_utils',
 'ovretl.containers_utils.tests',
 'ovretl.db_utils',
 'ovretl.employees_utils',
 'ovretl.employees_utils.tests',
 'ovretl.kronos_propositions_utils',
 'ovretl.kronos_propositions_utils.tests',
 'ovretl.loads_utils',
 'ovretl.loads_utils.tests',
 'ovretl.performances_utils',
 'ovretl.performances_utils.tests',
 'ovretl.prices_utils',
 'ovretl.prices_utils.features_functions',
 'ovretl.prices_utils.tests',
 'ovretl.shipment_orchestration_utils',
 'ovretl.shipment_orchestration_utils.tests',
 'ovretl.shipments_utils',
 'ovretl.shipments_utils.tests',
 'ovretl.shipowners_utils',
 'ovretl.shipowners_utils.__tests__',
 'ovretl.tasks_utils',
 'ovretl.tasks_utils.tests',
 'ovretl.tracking_utils',
 'ovretl.tracking_utils.tests',
 'ovretl.transit_times',
 'ovretl.transit_times.tests']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.14.48,<2.0.0',
 'botocore>=1.17.48,<2.0.0',
 'pandas==0.23.4',
 'psycopg2-binary>=2.8.5,<3.0.0',
 'snapshottest>=0.5.1,<0.6.0',
 'time-machine==2.1.0']

setup_kwargs = {
    'name': 'ovretl',
    'version': '5.8.1',
    'description': 'Python package for Ovrsea ETL',
    'long_description': '',
    'author': 'nicolas67',
    'author_email': 'nicolas@ovrsea.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1',
}


setup(**setup_kwargs)
