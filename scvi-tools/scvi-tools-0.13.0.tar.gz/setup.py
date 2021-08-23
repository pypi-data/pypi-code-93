# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scvi',
 'scvi.data',
 'scvi.data._built_in_data',
 'scvi.dataloaders',
 'scvi.distributions',
 'scvi.external',
 'scvi.external.cellassign',
 'scvi.external.gimvi',
 'scvi.external.solo',
 'scvi.external.stereoscope',
 'scvi.model',
 'scvi.model.base',
 'scvi.module',
 'scvi.module.base',
 'scvi.nn',
 'scvi.train',
 'scvi.utils']

package_data = \
{'': ['*']}

install_requires = \
['anndata>=0.7.5',
 'h5py>=2.9.0',
 'ipywidgets',
 'numba>=0.41.0',
 'numpy>=1.17.0',
 'openpyxl>=3.0',
 'pandas>=1.0',
 'pyro-ppl>=1.6.0',
 'pytorch-lightning>=1.3,<1.4',
 'rich>=9.1.0',
 'scikit-learn>=0.21.2',
 'torch>=1.8.0',
 'tqdm>=4.56.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0'],
 'dev': ['black>=20.8b1',
         'codecov>=2.0.8',
         'flake8>=3.7.7',
         'isort>=5.7',
         'jupyter>=1.0',
         'loompy>=3.0.6',
         'nbconvert>=5.4.0',
         'nbformat>=4.4.0',
         'pre-commit>=2.7.1',
         'pytest>=4.4',
         'scanpy>=1.6'],
 'docs': ['nbsphinx',
          'nbsphinx-link',
          'pydata-sphinx-theme>=0.4.3',
          'scanpydoc>=0.5',
          'sphinx>=3.4',
          'sphinx-autodoc-typehints',
          'sphinx-gallery>0.6',
          'sphinx-tabs',
          'sphinx_copybutton<=0.3.1'],
 'docs:python_version < "3.8"': ['typing_extensions'],
 'docs:python_version >= "3.7"': ['ipython>=7.20'],
 'tutorials': ['leidenalg',
               'loompy>=3.0.6',
               'python-igraph',
               'scanpy>=1.6',
               'scikit-misc>=0.1.3']}

setup_kwargs = {
    'name': 'scvi-tools',
    'version': '0.13.0',
    'description': 'Deep probabilistic analysis of single-cell omics data.',
    'long_description': '<img src="https://github.com/YosefLab/scvi-tools/blob/master/docs/_static/scvi-tools-horizontal.svg?raw=true" width="400" alt="scvi-tools">\n\n[![Stars](https://img.shields.io/github/stars/YosefLab/scvi-tools?logo=GitHub&color=yellow)](https://github.com/YosefLab/scvi-tools/stargazers)\n[![PyPI](https://img.shields.io/pypi/v/scvi-tools.svg)](https://pypi.org/project/scvi-tools)\n[![Documentation Status](https://readthedocs.org/projects/scvi/badge/?version=latest)](https://scvi.readthedocs.io/en/stable/?badge=stable)\n![Build\nStatus](https://github.com/YosefLab/scvi-tools/workflows/scvi-tools/badge.svg)\n[![Coverage](https://codecov.io/gh/YosefLab/scvi-tools/branch/master/graph/badge.svg)](https://codecov.io/gh/YosefLab/scvi-tools)\n[![Code\nStyle](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)\n[![Downloads](https://pepy.tech/badge/scvi-tools)](https://pepy.tech/project/scvi-tools)\n[![Join the chat at https://gitter.im/scvi-tools/development](https://badges.gitter.im/scvi-tools/development.svg)](https://gitter.im/scvi-tools/development?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)\n\n[scvi-tools](https://scvi-tools.org/) (single-cell variational inference\ntools) is a package for probabilistic modeling of single-cell omics\ndata, built on top of [PyTorch](https://pytorch.org) and\n[AnnData](https://anndata.readthedocs.io/en/latest/).\n\n# Available implementations of single-cell omics models\n\nscvi-tools contains scalable implementations of several models that\nfacilitate a broad number of tasks across many omics, including:\n\n-   [scVI](https://rdcu.be/bdHYQ) for analysis of single-cell RNA-seq\n    data, as well as its improved differential expression\n    [framework](https://www.biorxiv.org/content/biorxiv/early/2019/10/04/794289.full.pdf).\n-   [scANVI](https://www.biorxiv.org/content/biorxiv/early/2019/01/29/532895.full.pdf)\n    for cell annotation of scRNA-seq data using semi-labeled examples.\n-   [totalVI](https://www.biorxiv.org/content/10.1101/2020.05.08.083337v1.full.pdf)\n    for analysis of CITE-seq data.\n-   [gimVI](https://arxiv.org/pdf/1905.02269.pdf) for imputation of\n    missing genes in spatial transcriptomics from scRNA-seq data.\n-   [AutoZI](https://www.biorxiv.org/content/biorxiv/early/2019/10/10/794875.full.pdf)\n    for assessing gene-specific levels of zero-inflation in scRNA-seq\n    data.\n-   [LDVAE](https://www.biorxiv.org/content/10.1101/737601v1.full.pdf)\n    for an interpretable linear factor model version of scVI.\n-   [Stereoscope](https://www.nature.com/articles/s42003-020-01247-y)\n    for deconvolution of spatial transcriptomics data.\n-   [DestVI](https://www.biorxiv.org/content/10.1101/2021.05.10.443517v1) for multi-resolution deconvolution\n    of spatial transcriptomics data.\n-   [peakVI](https://www.biorxiv.org/content/10.1101/2021.04.29.442020v1) for analysis of scATAC-seq data.\n-   [scArches](https://www.biorxiv.org/content/10.1101/2020.07.16.205997v1)\n    for transfer learning from one single-cell atlas to a query dataset\n    (currently supports scVI, scANVI and TotalVI).\n-   [CellAssign](https://www.nature.com/articles/s41592-019-0529-1) for\n    reference-based annotation of scRNA-seq data.\n-   [Solo](https://www.sciencedirect.com/science/article/pii/S2405471220301952)\n    for doublet detection in scRNA-seq data.\n\nAll these implementations have a high-level API that interacts with\n[scanpy](http://scanpy.readthedocs.io/), standard save/load functions,\nand support GPU acceleration.\n\n# Rapid development of novel probabilistic models\n\nscvi-tools contains the building blocks to develop and deploy novel probablistic\nmodels. These building blocks are powered by popular probabilistic and\nmachine learning frameworks such as [PyTorch\nLightning](https://www.pytorchlightning.ai/) and\n[Pyro](https://pyro.ai/).\n\nWe recommend checking out the [skeleton\nrepository](https://github.com/YosefLab/scvi-tools-skeleton) as a\nstarting point for developing new models into scvi-tools.\n\n# Basic installation\n\nFor conda,\n```\nconda install scvi-tools -c bioconda -c conda-forge\n```\nand for pip,\n```\npip install scvi-tools\n```\nPlease be sure to install a version of [PyTorch](https://pytorch.org/) that is compatible with your GPU (if applicable).\n\n# Resources\n\n-   Tutorials, API reference, and installation guides are available in\n    the [documentation](https://docs.scvi-tools.org/).\n-   For discussion of usage, check out our\n    [forum](https://discourse.scvi-tools.org).\n-   Please use the [issues](https://github.com/YosefLab/scvi-tools/issues) to submit bug reports.\n-   If you\\\'d like to contribute, check out our [contributing\n    guide](https://docs.scvi-tools.org/en/stable/contributing/index.html).\n-   If you find a model useful for your research, please consider citing\n    the corresponding publication (linked above).\n\n# Reference\n\nIf you used scvi-tools in your research, please consider citing\n\n```\n@article{Gayoso2021scvitools,\n\tauthor = {Gayoso, Adam and Lopez, Romain and Xing, Galen and Boyeau, Pierre and Wu, Katherine and Jayasuriya, Michael and Mehlman, Edouard and Langevin, Maxime and Liu, Yining and Samaran, Jules and Misrachi, Gabriel and Nazaret, Achille and Clivio, Oscar and Xu, Chenling and Ashuach, Tal and Lotfollahi, Mohammad and Svensson, Valentine and da Veiga Beltrame, Eduardo and Talavera-Lopez, Carlos and Pachter, Lior and Theis, Fabian J and Streets, Aaron and Jordan, Michael I and Regier, Jeffrey and Yosef, Nir},\n\ttitle = {scvi-tools: a library for deep probabilistic analysis of single-cell omics data},\n\tyear = {2021},\n\tdoi = {10.1101/2021.04.28.441833},\n\tpublisher = {Cold Spring Harbor Laboratory},\n\tURL = {https://www.biorxiv.org/content/early/2021/04/29/2021.04.28.441833},\n\teprint = {https://www.biorxiv.org/content/early/2021/04/29/2021.04.28.441833.full.pdf},\n\tjournal = {bioRxiv}\n}\n```\n',
    'author': 'Romain Lopez',
    'author_email': 'romain_lopez@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/YosefLab/scvi-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
