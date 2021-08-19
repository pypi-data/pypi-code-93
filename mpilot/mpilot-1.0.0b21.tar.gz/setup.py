# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mpilot',
 'mpilot.cli',
 'mpilot.libraries',
 'mpilot.libraries.eems',
 'mpilot.libraries.eems.csv',
 'mpilot.libraries.eems.netcdf',
 'mpilot.parser']

package_data = \
{'': ['*']}

install_requires = \
['click<8.0', 'packaging', 'ply>=3.11,<4.0', 'six']

extras_require = \
{':python_version >= "2.7" and python_version < "2.8"': ['numpy<=1.16.6'],
 ':python_version >= "3.6"': ['numpy>=1.19.4,<2.0.0'],
 'netcdf': ['netCDF4<1.5.6']}

entry_points = \
{'console_scripts': ['mpilot = mpilot.cli.mpilot:main']}

setup_kwargs = {
    'name': 'mpilot',
    'version': '1.0.0b21',
    'description': 'MPilot is a plugin-based, environmental modeling framework',
    'long_description': '# MPilot (beta)\nMPilot is a plugin-based, environmental modeling framework based on a bottom-up, many-to-many workflow that can be \nrepresented by a directed (not iterating) graph. MPilot is descended from the Environmental Evaluation Modeling System \n(EEMS), which was initially a fuzzy logic modeling package based on EMDS.\n\n[MPilot Documentation](https://consbio.github.io/mpilot/)\n\n# Installing\n\nMPilot with EEMS can be installed with `pip`:\n\n```bash\n$ pip install mpilot\n```\n\nIn order to run MPilot with NetCDF datasets, you\'ll need to install the NetCDF variant:\n\n```bash\n$ pip install mpilot[netcdf]\n```\n\n# Creating models\nMPilot models are contained in "command files", using a simple scripting language. Here is an example model, which \nloads two columns of integer data from a CSV file, sums them, and writes the result to a second CSV file.\n\n```text\nA = EEMSRead(\n    InFileName = "input.csv",\n    InFieldName = "A",\n    DataType = "Integer"\n)\nB = EEMSRead(\n    InFileName = "input.csv",\n    InFieldName = "B",\n    DataType = "Integer"\n)\nAPlusB = Sum(\n    InFieldNames = [A, B]\n)\nOut = EEMSWrite(\n    OutFileName = "output.csv",\n    OutFieldNames = [A, B, APlusB]\n)\n```\n\n# Running models\n\nModels are run using the included `mpilot` program. The following commands will run a model using the EEMS CSV library \nand using the EEMS NetCDF library respectively:\n\n```bash\n$ mpilot eems-csv model.mpt\n$ mpilot eems-netcdf model.mpt\n```\n',
    'author': 'Conservation Biology Institute',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://consbio.github.io/mpilot/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
}


setup(**setup_kwargs)
