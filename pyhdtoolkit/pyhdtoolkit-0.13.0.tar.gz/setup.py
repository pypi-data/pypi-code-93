# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyhdtoolkit',
 'pyhdtoolkit.cpymadtools',
 'pyhdtoolkit.maths',
 'pyhdtoolkit.models',
 'pyhdtoolkit.optics',
 'pyhdtoolkit.plotting',
 'pyhdtoolkit.utils']

package_data = \
{'': ['*']}

install_requires = \
['cpymad>=1.6,<2.0',
 'loguru<1.0',
 'matplotlib>=3.0,<4.0',
 'numpy>=1.19,<2.0',
 'pandas>=1.0,<2.0',
 'pendulum>=2.0,<3.0',
 'pydantic>=1.0,<2.0',
 'rich>=10.0,<11.0',
 'scipy>=1.4,<2.0',
 'tfs-pandas>=2.0,<3.0']

setup_kwargs = {
    'name': 'pyhdtoolkit',
    'version': '0.13.0',
    'description': 'An all-in-one toolkit package to easy my Python work in my PhD.',
    'long_description': '<h1 align="center">\n  <b>PyhDToolkit</b>\n</h1>\n\n<p align="center">\n  <!-- PyPi Version -->\n  <a href="https://pypi.org/project/pyhdtoolkit">\n    <img alt="PyPI Version" src="https://img.shields.io/pypi/v/pyhdtoolkit?label=PyPI&logo=PyPI">\n  </a>\n\n  <!-- Github Release -->\n  <a href="https://github.com/fsoubelet/PyhDToolkit/releases">\n    <img alt="Github Release" src="https://img.shields.io/github/v/release/fsoubelet/PyhDToolkit?color=orange&label=Release&logo=Github">\n  </a>\n\n  <br/>\n\n  <!-- Github Actions Build -->\n  <a href="https://github.com/fsoubelet/PyhDToolkit/actions?query=workflow%3A%22Cron+Testing%22">\n    <img alt="Github Actions" src="https://github.com/fsoubelet/PyhDToolkit/workflows/Tests/badge.svg">\n  </a>\n\n  <!-- Code Coverage -->\n  <a href="https://codecov.io/gh/fsoubelet/PyhDToolkit">\n    <img src="https://codecov.io/gh/fsoubelet/PyhDToolkit/branch/master/graph/badge.svg?token=6SO90F2MJI"/>\n  </a>\n\n  <!-- Docker Image -->\n  <a href="https://hub.docker.com/r/fsoubelet/simenv">\n    <img alt="Docker Image" src="https://img.shields.io/docker/image-size/fsoubelet/simenv?label=Docker&sort=date">\n  </a>\n\n  <br/>\n\n  <!-- Code style -->\n  <a href="https://github.com/psf/Black">\n    <img alt="Code Style" src="https://img.shields.io/badge/Code%20Style-Black-9cf.svg">\n  </a>\n\n  <!-- Linter -->\n  <a href="https://github.com/PyCQA/pylint">\n    <img alt="Linter" src="https://img.shields.io/badge/Linter-Pylint-ce963f.svg">\n  </a>\n\n  <!-- Build tool -->\n  <a href="https://github.com/python-poetry/poetry">\n    <img alt="Build tool" src="https://img.shields.io/badge/Build%20Tool-Poetry-4e5dc8.svg">\n  </a>\n\n  <!-- Test runner -->\n  <a href="https://github.com/pytest-dev/pytest">\n    <img alt="Test runner" src="https://img.shields.io/badge/Test%20Runner-Pytest-ce963f.svg">\n  </a>\n\n  <!-- License -->\n  <a href="https://github.com/fsoubelet/PyhDToolkit/blob/master/LICENSE">\n    <img alt="License" src="https://img.shields.io/github/license/fsoubelet/PyhDToolkit?color=9cf&label=License">\n  </a>\n</p>\n\n<p align="center">\n  ♻️ An all-in-one package for Python work in my PhD ♻️\n</p>\n\n<p align="center">\n  <!-- General DOI -->\n  <a href="https://zenodo.org/badge/latestdoi/227081702">\n    <img alt="DOI" src="https://zenodo.org/badge/227081702.svg">\n  </a>\n</p>\n\n<p align="center">\n  <a href="https://www.python.org/">\n    <img alt="Made With Python" src="https://forthebadge.com/images/badges/made-with-python.svg">\n  </a>\n</p>\n\nLink to [documentation].\n\n## License\n\nCopyright &copy; 2019 Felix Soubelet. [MIT License](LICENSE)\n\n[documentation]: https://fsoubelet.github.io/PyhDToolkit/\n',
    'author': 'Felix Soubelet',
    'author_email': 'felix.soubelet@cern.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fsoubelet/PyhDToolkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
