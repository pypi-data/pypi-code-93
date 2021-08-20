# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gordo_dataset',
 'gordo_dataset.data_provider',
 'gordo_dataset.data_provider.resources',
 'gordo_dataset.file_system']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'azure-datalake-store>=0.0.51,<0.0.52',
 'azure-identity>=1.4.0,<2.0.0',
 'azure-storage-file-datalake>=12.1.2,<13.0.0',
 'cachetools>=4.1.0,<5.0.0',
 'cryptography>=3.4.0,<4.0.0',
 'influxdb>=5.3.0,<6.0.0',
 'marshmallow>=3.3.0,<4.0.0',
 'numexpr>=2.7.1,<3.0.0',
 'numpy==1.19.5',
 'pandas>=1.0.3,<2.0.0',
 'pyarrow>=0.17.1,<0.18.0',
 'scikit-learn>=0.23.2,<0.24.0',
 'typing_extensions>=3.7.4,<4.0.0',
 'xarray>=0.16.2,<0.17.0']

setup_kwargs = {
    'name': 'gordo-dataset',
    'version': '2.7.0',
    'description': 'Gordo datasets and data providers',
    'long_description': '# Gordo dataset\n\ngordo dataset library essential to build datasets and data providers for [gordo](https://github.com/equinor/gordo) projects.\n\n## Usage\n\n### Data provider\n\nExtend [GordoBaseDataProvider](gordo_dataset/data_provider/base.py) to adapt it to your data source.\n\nSee examples [NcsReader](gordo_data_set/data_provider/ncs_reader.py) that reads either parquet or csv files from Azure Datalake v1.\n\n### Dataset\n\nExtend [GordoBaseDataset](gordo_dataset/base.py).\n\nSee example for [TimeSeriesDataset](gordo_dataset/datasets.py) that arranges the data into consecutive times series.\n\n### Install\n\n`pip install gordo-dataset`\n\n### Uninstall\n\n`pip uninstall gordo-datset`\n',
    'author': 'Equinor ASA',
    'author_email': 'fg_gpl@equinor.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/equinor/gordo-dataset',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
