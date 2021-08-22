# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spectrafit', 'spectrafit.test']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'lmfit>=1.0.2,<2.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numdifftools>=0.9.40,<0.10.0',
 'numpy>=1.21.1,<2.0.0',
 'openpyxl>=3.0.7,<4.0.0',
 'pandas>=1.3.0,<2.0.0',
 'scipy>=1.7.0,<2.0.0',
 'seaborn>=0.11.1,<0.12.0',
 'statsmodels>=0.12.2,<0.13.0',
 'tabulate>=0.8.9,<0.9.0',
 'toml>=0.10.2,<0.11.0',
 'tqdm>=4.61.2,<5.0.0']

entry_points = \
{'console_scripts': ['spectrafit = spectrafit.spectrafit:command_line_runner']}

setup_kwargs = {
    'name': 'spectrafit',
    'version': '0.3.1',
    'description': 'Fast fitting of 2D-Spectra with established routines',
    'long_description': "# SpectraFit\n\n`SpectraFit` is a command line tool for quick data fitting based on the regular\nexpression of distribution and linear functions. Furthermore, it can be also\nused as a module in existing python code. A previous version of `SpectraFit` was\nused for the following publication:\n\n- [Measurement of the Ligand Field Spectra of Ferrous and Ferric Iron Chlorides Using 2p3d RIXS](https://pubs.acs.org/doi/abs/10.1021/acs.inorgchem.7b00940)\n\nNow, it is completely rewritten and is more flexible.\n\n## Scope:\n\n- Fitting of 2d data\n- Using established and advanced solver methods\n- Extensibility of the fitting function\n- Guarantee traceability of the fitting results\n- Saving all results for publications in a `CSV`-format\n- Saving all results in a NoSQL-format (`JSON`) for project management\n- Having an API interface for Graph-databases\n\n## Installation:\n\nvia pip:\n\n```shell\npip install spectrafit\n```\n\n## Usage:\n\n`SpectraFit` needs as command line tool only two things:\n\n1. The reference data, which should be fitted.\n2. The input file, which contains the initial model.\n\nAs model files [json](https://en.wikipedia.org/wiki/JSON),\n[toml](https://en.wikipedia.org/wiki/TOML), and\n[yaml](https://en.wikipedia.org/wiki/YAML) are supported. By making use of the\npython `**kwargs` feature, the input file can call most of the following\nfunctions of [LMFIT](https://lmfit.github.io/lmfit-py/index.html). LMFIT is the\nworkhorse for the fit optimization, which is macro wrapper based on:\n\n1. [NumPy](https://www.numpy.org/)\n2. [SciPy](https://www.scipy.org/)\n3. [uncertainties](https://pythonhosted.org/uncertainties/)\n\nIn case of `SpectraFit`, we have further extend the package by:\n\n1. [Pandas](https://pandas.pydata.org/)\n2. [Statsmodels](https://www.statsmodels.org/stable/index.html)\n3. [numdifftools](https://github.com/pbrod/numdifftools)\n4. [Matplotlib](https://matplotlib.org/) in combination with\n   [Seaborn](https://seaborn.pydata.org/)\n\n```shell\nspectrafit data_file.txt input_file.json\n```\n\n```shell\nspectrafit -h\nusage: spectrafit [-h] [-o OUTFILE] [-i INPUT] [-ov] [-disp] [-e0 ENERGY_START] [-e1 ENERGY_STOP] [-s SMOOTH] [-sh SHIFT] [-c COLUMN COLUMN] [-sep {    ,,,;,:,|, ,s+}] [-dec {.,,}] [-hd HEADER] [-np] [-v] [-vb] infile\n\nFast Fitting Program for ascii txt files.\n\npositional arguments:\n  infile                Filename of the specta data\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -o OUTFILE, --outfile OUTFILE\n                        Filename for the export, default to set to 'spectrafit_results'.\n  -i INPUT, --input INPUT\n                        Filename for the input parameter, default to set to 'fitting_input.toml'.Supported fileformats are: '*.json', '*.yml', '*.yaml', and '*.toml'\n  -ov, --oversampling   Oversampling the spectra by using factor of 5; default to False.\n  -disp                 Hole or splitted Table on the Screen; default to 'hole'.\n  -e0 ENERGY_START, --energy_start ENERGY_START\n                        Starting energy in eV; default to start of energy.\n  -e1 ENERGY_STOP, --energy_stop ENERGY_STOP\n                        Ending energy in eV; default to end of energy.\n  -s SMOOTH, --smooth SMOOTH\n                        Number of smooth points for lmfit; default to 0.\n  -sh SHIFT, --shift SHIFT\n                        Constant applied energy shift; default to 0.0.\n  -c COLUMN COLUMN, --column COLUMN COLUMN\n                        Selected columns for the energy- and intensity-values; default to 0 for energy (x-axis) and 1 for intensity (y-axis).\n  -sep {        ,,,;,:,|, ,s+}, --seperator {   ,,,;,:,|, ,s+}\n                        Redefine the type of seperator; default to ' '.\n  -dec {.,,}, --decimal {.,,}\n                        Type of decimal seperator; default to '.'.\n  -hd HEADER, --header HEADER\n                        Selected the header for the dataframe; default to None.\n  -np, --noplot         No plotting the spectra and the fit of `spectrafit`.\n  -v, --version         Display the current version of `spectrafit`.\n  -vb, --verbose        Display the initial configuration parameters as a dictionary.\n```\n\n## Documentation:\n\nPlease see the [extended documentation](https://anselmoo.github.io/spectrafit/)\nfor the full usage of `SpectraFit`.\n",
    'author': 'Anselm Hahn',
    'author_email': 'Anselm.Hahn@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://anselmoo.github.io/spectrafit/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
