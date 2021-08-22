# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mars_mcd_helper']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'numpy>=1.21.2,<2.0.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['mars-mcd-helper = mars_mcd_helper.cli:main']}

setup_kwargs = {
    'name': 'mars-mcd-helper',
    'version': '0.0.7',
    'description': 'Utilities for retrieving and processing data from the Mars Climate Database',
    'long_description': '# mars-MCD-helper\n\n[![ci](https://github.com/2e0byo/mars-mcd-helper/workflows/ci/badge.svg)](https://github.com/2e0byo/mars-mcd-helper/actions?query=workflow%3Aci)\n[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://2e0byo.github.io/mars-mcd-helper/)\n[![pypi version](https://img.shields.io/pypi/v/mars-mcd-helper.svg)](https://pypi.org/project/mars-mcd-helper/)\n[![gitter](https://badges.gitter.im/join%20chat.svg)](https://gitter.im/mars-mcd-helper/community)\n\nUtilities for retrieving and processing data from the Mars Climate Database.\n\nCurrently nothing more than an interface to\n[www-mars.lmd.jussie.fr](http://www-mars.lmd.jussieu.fr/mcd_python).  Note that\nthis tool is not in any way affiliated with that excellent project.  It is\nsimply a requests-based scraper.  Overuse or repetitive fetching could result in\nratelimiting or banning from `jussieu.fr`.\n\n\n\n## Usage\n\n```python\nfrom mars_mcd_helper import fetch_data, read_ascii_data\noutf, imgf = fetch_data(outdir=".", get_img=True, ls=87.4)\nsections = read_ascii_data(outf)\nprint("Image to compare at", imgf)\n```\n\n## Requirements\n\nmars-MCD-helper requires Python 3.7 or above.\n\n<details>\n<summary>To install Python 3.7, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>\n\n```bash\n# install pyenv\ngit clone https://github.com/pyenv/pyenv ~/.pyenv\n\n# setup pyenv (you should also put these three lines in .bashrc or similar)\nexport PATH="${HOME}/.pyenv/bin:${PATH}"\nexport PYENV_ROOT="${HOME}/.pyenv"\neval "$(pyenv init -)"\n\n# install Python 3.7\npyenv install 3.7.12\n\n# make it available globally\npyenv global system 3.7.12\n```\n</details>\n\n## Installation\n\nWith `pip`:\n```bash\npython -m pip install mars-mcd-helper # or\npython3.7 -m pip install mars-mcd-helper\n```\n\nWith [`pipx`](https://github.com/pipxproject/pipx):\n```bash\npython3.7 -m pip install --user pipx\n\npipx install --python python3.7 mars-mcd-helper\n```\n\n',
    'author': 'John Morris',
    'author_email': 'john.morris@durham.ac.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/2e0byo/mars-mcd-helper',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
