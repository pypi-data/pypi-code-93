# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['spatstat_interface']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.20.3,<2.0.0',
 'pandas>=1.2.4,<2.0.0',
 'rpy2>=3.4.5,<4.0.0']

extras_require = \
{'notebook': ['jupyter>=1.0.0,<2.0.0', 'ipykernel>=5.5.3,<6.0.0']}

setup_kwargs = {
    'name': 'spatstat-interface',
    'version': '0.1.0a0',
    'description': 'Simple Python interface with the spatstat R package using rpy2',
    'long_description': '# spatstat-interface\n\n[![Build](https://github.com/For-a-few-DPPs-more/spatstat-interface/actions/workflows/main.yml/badge.svg)](https://github.com/For-a-few-DPPs-more/spatstat-interface/actions/workflows/main.yml)\n[![codecov](https://codecov.io/gh/For-a-few-DPPs-more/spatstat-interface/branch/main/graph/badge.svg?token=BHTI6L66P2)](https://codecov.io/gh/For-a-few-DPPs-more/spatstat-interface)\n\nSimple Python interface with the spatial statistics R package [spatstat](https://github.com/spatstat/spatstat) using [rpy2](https://github.com/rpy2/rpy2).\n\n## Dependecies\n\n* [R](https://www.r-project.org/) (programming language), \n* Python dependencies are listed in the [pyproject.toml](https://github.com/For-a-few-DPPs-more/spatstat-interface/blob/main/pyproject.toml) file.\n\n## Installation\n\n1) To install the lastest test version from [TestPyPi](https://test.pypi.org/project/spatstat-interface/)\n\n```bash\npip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ spatstat-interface\n```\n\n2) To install the latest development version from [GitHub](https://github.com/For-a-few-DPPs-more/spatstat-interface)\n\n```bash\ngit clone https://github.com/For-a-few-DPPs-more/spatstat-interface.git\ncd spatstat-interface\npip install .\n```\n\n3) To install the latest stable version **once the package will be available on on [PyPI](https://pypi.org/)**\n\n```bash\npip install spatstat-interface\n```\n\n## Documentation\n\n* [notebooks](https://github.com/For-a-few-DPPs-more/spatstat-interface/blob/main/notebooks) for detailed examples\n* [rpy2 documentation](https://rpy2.github.io/doc.html)\n* [spatstat documentation](https://rdocumentation.org/search?q=spatstat)\n\nThe [spatstat](https://github.com/spatstat/spatstat) package has recently been split into multiple subpackages and extensions.\n\nUsing `spatstat-interface` , subpackages and extensions are accessible in the following way\n\n```python\nfrom spatstat_interface import SpatstatInterface\nspatstat = SpatstatInterface(update=True)\n# spatstat.core is None\n# spatstat.geom is None\n\n# load/import subpackages or extensions\nspatstat.import_package("core", "geom", update=False)\nspatstat.core\nspatstat.geom\n```\n',
    'author': 'Guillaume Gautier',
    'author_email': 'guillaume.gga@gmail.com',
    'maintainer': 'Guillaume Gautier',
    'maintainer_email': 'guillaume.gga@gmail.com',
    'url': 'https://github.com/For-a-few-DPPs-more/spatstat-interface',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
