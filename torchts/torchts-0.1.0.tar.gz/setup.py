# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['torchts', 'torchts.nn', 'torchts.nn.models', 'torchts.utils']

package_data = \
{'': ['*']}

install_requires = \
['pytorch-lightning>=1.4.1,<2.0.0',
 'scipy>=1.7.1,<2.0.0',
 'torch>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'torchts',
    'version': '0.1.0',
    'description': 'Time series forecasting with PyTorch',
    'long_description': '<a href="https://rose-stl-lab.github.io/torchTS/">\n  <img width="350" src="./docs/source/_static/images/torchTS_logo.png" alt="TorchTS Logo" />\n</a>\n\n---\n\n[![Tests](https://github.com/Rose-STL-Lab/torchTS/workflows/Tests/badge.svg)](https://github.com/Rose-STL-Lab/torchTS/actions?query=workflow%3ATests)\n[![Quality](https://github.com/Rose-STL-Lab/torchTS/workflows/Quality/badge.svg)](https://github.com/Rose-STL-Lab/torchTS/actions?query=workflow%3AQuality)\n[![Docs](https://github.com/Rose-STL-Lab/torchTS/workflows/Docs/badge.svg)](https://github.com/Rose-STL-Lab/torchTS/actions?query=workflow%3ADocs)\n[![Codecov](https://img.shields.io/codecov/c/github/Rose-STL-Lab/torchTS?label=Coverage&logo=codecov)](https://app.codecov.io/gh/Rose-STL-Lab/torchTS)\n[![PyPI](https://img.shields.io/pypi/v/torchts?label=PyPI&logo=python)](https://pypi.org/project/torchts)\n[![License](https://img.shields.io/github/license/Rose-STL-Lab/torchTS?label=License)](LICENSE)\n\nTorchTS is a PyTorch-based library for time series data.\n\n***Currently under active development!***\n\n#### Why Time Series?\n\nTime series data modeling has broad significance in public health, finance and engineering. Traditional time series methods from statistics often rely on strong modeling assumptions, or are computationally expensive. Given the rise of large-scale sensing data and significant advances in deep learning, the goal of the project is to develop an efficient and user-friendly deep learning library that would benefit the entire research community and beyond.\n\n#### Why TorchTS?\n\nExisting time series analysis libraries include [statsmodels](https://www.statsmodels.org/stable/index.html) and [sktime](https://github.com/alan-turing-institute/sktime). However, these libraries only include traditional statistics tools such as ARMA or ARIMA, which do not have the state-of-the-art forecasting tools based on deep learning. [GluonTS](https://ts.gluon.ai/) is an open-source time series library developed by Amazon AWS, but is based on MXNet. [Pyro](https://pyro.ai/) is a probabilistic programming framework based on PyTorch, but is not focused on time series forecasting.\n\n## Installation\n\n### Installation Requirements\n\nTorchTS supports Python 3.7+ and has the following dependencies:\n\n- [PyTorch](https://pytorch.org/)\n- [PyTorch Lightning](https://pytorchlightning.ai/)\n- [SciPy](https://www.scipy.org/)\n\n### Installing the latest release\n\nThe latest release of TorchTS is easily installed either via `pip`:\n\n```bash\npip install torchts\n```\n\nor via [conda](https://docs.conda.io/projects/conda/) from the [conda-forge](https://conda-forge.org/) channel (coming soon):\n\n```bash\nconda install torchts -c conda-forge\n```\n\nYou can customize your PyTorch installation (i.e. CUDA version, CPU only option)\nby following the [PyTorch installation instructions](https://pytorch.org/get-started/locally/).\n\n***Important note for MacOS users:***\n\n- Make sure your PyTorch build is linked against MKL (the non-optimized version\n  of TorchTS can be up to an order of magnitude slower in some settings).\n  Setting this up manually on MacOS can be tricky - to ensure this works properly,\n  please follow the [PyTorch installation instructions](https://pytorch.org/get-started/locally/).\n- If you need CUDA on MacOS, you will need to build PyTorch from source. Please\n  consult the PyTorch installation instructions above.\n\n## Getting Started\n\nCheck out our [documentation](https://rose-stl-lab.github.io/torchTS/) and\n[tutorials](https://rose-stl-lab.github.io/torchTS/tutorials) (coming soon).\n\n## Citing TorchTS\n\nIf you use TorchTS, please cite the following paper (coming soon):\n\n> [TorchTS: A Framework for Efficient Time Series Modeling](TBD)\n\n```bibtex\n@inproceedings{TBD,\n  title={{TorchTS: A Framework for Efficient Time Series Modeling}},\n  author={TBD},\n  booktitle = {TBD},\n  year={TBD},\n  url = {TBD}\n}\n```\n\nSee [here](https://rose-stl-lab.github.io/torchTS/papers) (coming soon) for a selection of peer-reviewed papers that either build off of TorchTS or were integrated into TorchTS.\n\n## Contributing\n\nInterested in contributing to TorchTS? Please see the [contributing guide](CONTRIBUTING.md) to learn how to help out.\n\n## License\n\nTorchTS is [MIT licensed](LICENSE).\n',
    'author': 'TorchTS Team',
    'author_email': 'torchts@googlegroups.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rose-stl-lab.github.io/torchTS',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
