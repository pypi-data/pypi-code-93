# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nowcastlib',
 'nowcastlib.cli',
 'nowcastlib.pipeline',
 'nowcastlib.pipeline.process',
 'nowcastlib.pipeline.process.postprocess',
 'nowcastlib.pipeline.process.preprocess',
 'nowcastlib.pipeline.split',
 'nowcastlib.pipeline.sync']

package_data = \
{'': ['*']}

install_requires = \
['ConfigArgParse>=1.4.1,<2.0.0',
 'attrs>=21.2.0,<22.0.0',
 'cattrs>=1.7.1,<2.0.0',
 'importlib-metadata>=4.6.3,<5.0.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.19.2,<1.20.0',
 'pandas>=1.2.4,<2.0.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'skyfield>=1.39,<2.0']

entry_points = \
{'console_scripts': ['nowcastlib = nowcastlib.cli:main']}

setup_kwargs = {
    'name': 'nowcastlib',
    'version': '3.0.20',
    'description': '🧙🔧 Utils that can be reused and shared across and beyond the ESO Nowcast project',
    'long_description': '# Nowcast Library\n\n🧙\u200d♂️🔧 Utils that can be reused and shared across and beyond the ESO Nowcast\nproject\n\nThis is a public repository hosted on GitHub via a push mirror setup in the\n[internal ESO GitLab repository](https://gitlab.eso.org/gstarace/nowcastlib/)\n\n## Installation\n\nSimply run\n\n```console\npip install nowcastlib\n```\n\n## Usage and Documentation\n\nNowcast Library (nowcastlib) consists in a collection of functions organized in\nsubmodules (API) and a tool accessible via the command line (CLI). The latter is\nprimarily intended for accessing the Nowcast Library Pipeline, an opinionated\nyet configurable set of processing steps for wrangling data and evaluating\nmodels in a consistent and rigorous way. More information can be found on the\nnowcastlib pipeline index page\n([link to markdown](nowcastlib/pipeline/README.md) and\n[link to hosted docs](https://giuliostarace.com/nowcastlib/pipeline))\n\nPlease refer to the\n[examples folder](https://github.com/thesofakillers/nowcastlib/tree/master/examples)\non GitHub for usage examples.\n\n### API\n\nHere is a quick example of how one may import nowcastlib and access to one of\nthe functions:\n\n```python\n"""Example showing how to access compute_trig_fields function"""\nimport nowcastlib as ncl\nimport pandas as pd\nimport numpy as np\n\ndata_df = pd.DataFrame(\n    np.array([[0, 3, 4, np.NaN], [32, 4, np.NaN, 4], [56, 8, 0, np.NaN]]).T,\n    columns=["A", "B", "C"],\n    index=pd.date_range(start="1/1/2018", periods=4, freq="2min"),\n)\n\nresult = ncl.datasets.compute_trig_fields(data_df, ["A", "C"])\n```\n\nMore in-depth API documentation can be found\n[here](https://giuliostarace.com/nowcastlib/).\n\n### CLI\n\nSome of the library\'s functionality is bundled in configurable subcommands\naccessible via the terminal with the command `nowcastlib`:\n\n```console\nusage: nowcastlib [-h] [-v]\n                  {triangulate,preprocess,sync,postprocess,datapipe} ...\n\npositional arguments:\n  {triangulate,preprocess,sync,postprocess,datapipe}\n                        available commands\n    triangulate         Run `nowcastlib triangulate -h` for further help\n    preprocess          Run `nowcastlib preprocess -h` for further help\n    sync                Run `nowcastlib sync -h` for further help\n    postprocess         Run `nowcastlib postprocess -h` for further help\n    datapipe            Run `nowcastlib datapipe -h` for further help\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -v, --verbose         increase verbosity level from INFO to DEBUG\n```\n\n### Repository Structure\n\nThe following output is generated with `tree . -I \'dist|docs|*.pyc|__pycache__\'`\n\n```bash\n.\n├── LICENSE\n├── Makefile # currently used to build docs\n├── README.md\n├── de421.bsp # not committed\n├── docs/ # html files for the documentation static website\n├── examples\n│\xa0\xa0 ├── README.md\n│\xa0\xa0 ├── cli_triangulate_config.yaml\n│\xa0\xa0 ├── data/  # not committed\n│\xa0\xa0 ├── datasync.ipynb\n│\xa0\xa0 ├── output/ # not committed\n│\xa0\xa0 ├── pipeline_datapipe.json\n│\xa0\xa0 ├── pipeline_preprocess.json\n│\xa0\xa0 ├── pipeline_sync.json\n│\xa0\xa0 ├── signals.ipynb\n│\xa0\xa0 └── triangulation.ipynb\n├── images\n│\xa0\xa0 └── pipeline_flow.png\n├── nowcastlib # the actual source code for the library\n│\xa0\xa0 ├── __init__.py\n│\xa0\xa0 ├── cli\n│\xa0\xa0 │\xa0\xa0 ├── __init__.py\n│\xa0\xa0 │\xa0\xa0 └── triangulate.py\n│\xa0\xa0 ├── datasets.py\n│\xa0\xa0 ├── dynlag.py\n│\xa0\xa0 ├── gis.py\n│\xa0\xa0 ├── pipeline\n│\xa0\xa0 │\xa0\xa0 ├── README.md\n│\xa0\xa0 │\xa0\xa0 ├── __init__.py\n│\xa0\xa0 │\xa0\xa0 ├── cli.py\n│\xa0\xa0 │\xa0\xa0 ├── process\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 ├── __init__.py\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 ├── postprocess\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 │\xa0\xa0 ├── __init__.py\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 │\xa0\xa0 ├── cli.py\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 │\xa0\xa0 └── generate.py\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 ├── preprocess\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 │\xa0\xa0 ├── __init__.py\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 │\xa0\xa0 └── cli.py\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 └── utils.py\n│\xa0\xa0 │\xa0\xa0 ├── split\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 └── __init__.py\n│\xa0\xa0 │\xa0\xa0 ├── structs.py\n│\xa0\xa0 │\xa0\xa0 ├── sync\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 ├── __init__.py\n│\xa0\xa0 │\xa0\xa0 │\xa0\xa0 └── cli.py\n│\xa0\xa0 │\xa0\xa0 └── utils.py\n│\xa0\xa0 ├── signals.py\n│\xa0\xa0 └── utils.py\n├── poetry.lock # lock file generated by python poetry for dependency mgmt\n└── pyproject.toml # general information file, handled by python poetry\n```\n\n#### Directories and Files not Committed\n\nThere are a number of files and folders that are not committed due to their\nlarge and static nature that renders them inappropriate for git version control.\nThe following files and folder warrant a brief explanation.\n\n-   Certain functions (time since sunset, sun elevation) of the Nowcast Library\n    rely on the use of a .bsp file, containing information on the locations\n    through time of various celestial bodies in the sky. This file will be\n    automatically downloaded upon using one of these functions for the first\n    time.\n-   The examples scripts make use of a `data/` directory containing a series of\n    csv files. Most of the data used in the examples can be downloaded from the\n    [ESO Ambient Condition Database](http://archive.eso.org/cms/eso-data/ambient-conditions.html).\n    Users can then change the paths set in the examples to fit their needs. For\n    users interested in replicating the exact structure and contents of the data\n    directory, a compressed copy of it (1.08 GB) is available to ESO members\n    through\n    [this Microsoft Sharepoint link](https://europeansouthernobservatory.sharepoint.com/:u:/t/OpticalTurbulenceandWeatherNowcast/EeH844GlBgdBjc63uaPiO4ABrh7ylH54zH3dJV9WSIhakA?e=gPBWJ7).\n-   At times the examples show the serialization functionality of the nowcastlib\n    pipeline or need to output some data. In these situations the `output/`\n    directory in the examples folder is used.\n\n## Development Setup\n\nThis repository relies on [Poetry](https://python-poetry.org/) for tracking\ndependencies, building and publishing. It is therefore recommended that\ndevelopers [install poetry](https://python-poetry.org/docs/#installation) and\nmake use of it throughout their development of the project.\n\n### Dependencies\n\nMake sure you are in the right Python environment and run\n\n```console\npoetry install\n```\n\nThis reads [pyproject.toml](./pyproject.toml), resolves the dependencies, and\ninstalls them.\n\n### Deployment\n\nThe repository is published to [PyPi](https://pypi.org/), so to make it\naccessible via a `pip install` command as mentioned [earlier](#install).\n\nTo publish changes follow these steps. Ideally this process is automated via a\nCI tool triggered by a push/merge to the master branch:\n\n1. Optionally run\n   [`poetry version`](https://python-poetry.org/docs/cli/#version) with the\n   appropriate argument based on [semver guidelines](https://semver.org/).\n\n2. Update the documentation by running\n\n    ```console\n    make document\n    ```\n\n3. Prepare the package by running\n\n    ```console\n    poetry build\n    ```\n\n4. Ensure you have [TestPyPi](https://test.pypi.org/) and PyPi configured as\n   your poetry repositories:\n\n    ```console\n    poetry config repositories.testpypi https://test.pypi.org/legacy/\n    poetry config repositories.pypi https://pypi.org/\n    ```\n\n5. Publish the repository to TestPyPi, to see that everything works as expected:\n\n    ```console\n    poetry publish -r testpypi\n    ```\n\n6. Stage, commit and push your changes (to master) with git.\n7. Publish the repository to PyPi:\n\n    ```console\n    poetry publish -r pypi\n    ```\n\nUpon successful deployment, the library should be available for install via\n`pip`\n',
    'author': 'Giulio Starace',
    'author_email': 'giulio.starace@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://giuliostarace.com/nowcastlib/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
