# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bigquery_dry_run']

package_data = \
{'': ['*']}

install_requires = \
['google-cloud-bigquery>=2.13.1,<3.0.0', 'pytz>=2021.1,<2022.0']

entry_points = \
{'console_scripts': ['bqdry = bigquery_dry_run.app:run']}

setup_kwargs = {
    'name': 'bigquery-dry-run',
    'version': '0.3.1',
    'description': 'This package is used to perform a BigQuery dry run of all `.sql` files in a folder and its subfolders.',
    'long_description': '# Overview\n\nThis application is used to perform a BigQuery dry run of all `.sql` files in a folder and its subfolders.\n\nIts purpose it so ensure that all SQL files do not have any syntactic errors and make it easier for team members to quickly check a large number of files.\n\n# GCP configuration\n\nAllowing access to GCP should be done following one of the methods detailed in the [GCP documentation.](https://cloud.google.com/docs/authentication) \n\nThe application will rely on your environment having been set up for authentication to GCP (e.g. through `gcloud init` or `environement variable` containing service account credentials), it does not provide a mechanism to receive authentication credentials directly.\n\n# Usage\n\nThe application will install a shell command called `bqdry` which is simply passed a folder. It will then traverse the folder and perform a dry run of all `.sql` files found in the folder and any sub folders. The results will be displayed on in the terminal.\n\nFor example:\n```\n$ bqdry my-awesome-project\n\n>File: my-awesome-project/demo.sql\n>  Result: Failed\n>  Errors: None\n>\n>Total: 3\n>Succeeded: 2\n>Failed: 1\n```\n\n`bqdry -h` will provide usage information. E.g.\n\n```\nusage: bqdry [-h] [-t THREADS] [-v] folder\n\nDry run of all `.sql` files in folder and subfolders.\n\npositional arguments:\n  folder                Top level folder to start scanning for `.sql` files.\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -t THREADS, --threads THREADS\n                        Number of threads for concurrent running of queries. Defaults to 2.\n  -v, --verbose         Show all file results, not just failures.\n```\n\n\n\n\n',
    'author': 'Christo Olivier',
    'author_email': 'mail@christoolivier.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<3.10',
}


setup(**setup_kwargs)
