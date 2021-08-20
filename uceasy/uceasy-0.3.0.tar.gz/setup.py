# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['uceasy']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0,<9.0']

entry_points = \
{'console_scripts': ['uceasy = uceasy.console:cli']}

setup_kwargs = {
    'name': 'uceasy',
    'version': '0.3.0',
    'description': 'Wrapper for the Phyluce phylogenomics software package',
    'long_description': '<p>\n    <img src="docs/img/uceasy_logo.png" height="200px">\n\n</p>\n\n[![Tests](https://github.com/uceasy/uceasy/workflows/Tests/badge.svg)](https://github.com/uceasy/uceasy/actions?workflow=Tests)\n[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=uceasy_uceasy&metric=alert_status)](https://sonarcloud.io/dashboard?id=uceasy_uceasy)\n[![DOI](https://zenodo.org/badge/203415455.svg)](https://zenodo.org/badge/latestdoi/203415455)\n\n# UCEasy: a software package based on good practices in scientific computing for phylogenetic analysis of UCEs\n\n\n__UCEasy__ is a wrapper to automate manual procedures of the [PHYLUCE](https://phyluce.readthedocs.io/en/latest) software package by abstracting the pipeline steps into 3 major commands and choosing sensible defaults for its command-line options, easing the execution and improving reproducibility.\n\n\nAt the moment, the only software package for analysing [ultraconserved elements](https://www.ultraconserved.org/) (UCEs) is PHYLUCE, but its execution can be quite challenging especially for non-computer experts.\n__UCEasy__ is a convenient tool that automates the execution of common tasks for most types of UCE analysis, these being Quality Control, Assembly and UCE Processing.\n\nFor more information check out our [Wiki](https://github.com/uceasy/uceasy/wiki).\n## Installation Guide\n### Dependencies\n* Python ^3.7\n* PHYLUCE 1.6.* (1.7 not supported yet)\n\nInstall the package from [PyPI](https://pypi.org/project/uceasy/):\n```\n$ pip install uceasy\n```\nThen, make sure you have a working installation of PHYLUCE, check out the installation guide at [PHYLUCE\'s documentation](https://phyluce.readthedocs.io/en/latest/installation.html).\n\n\n## Workflow\nThe operations [Quality Control](https://github.com/uceasy/uceasy/wiki/QualityControl), [Assembly](https://github.com/uceasy/uceasy/wiki/Assembly) and [Phylogenomics](https://github.com/uceasy/uceasy/wiki/Phylogenomics) represent the following workflow.\n\n<p>\n    <img src="docs/img/workflow.png" height="500px">\n\n</p>\n\nThe colored boxes are UCEasy CLI commands.\n```\n$ uceasy quality-control\n$ uceasy assembly\n$ uceasy phylogenomics\n```\nExplore the options for these commands with the `--help` flag.<br>\n\nFor a guide of how to use UCEasy see: [Tutorial](https://github.com/uceasy/uceasy/wiki/Tutorial).\n\n\n## Acknowledgements\n\nWe thank the following institutions, which contributed to ensuring the success of our work:\n\nMinistério da Ciência, Tecnologia, Inovação e Comunicação (MCTIC)\n\nMuseu Paraense Emílio Goeldi (MPEG)\n\nInstituto Nacional de Pesquisas da Amazônia (INPA)\n\nCentro Universitário do Estado do Pará (CESUPA)\n\n## Funding\n\n This research was supported  by Conselho Nacional de Desenvolvimento Científico e Tecnológico - CNPq (fellowships 149985/2018-5; 129954/2018-7).\n\n## Authors\n\n Caio Vinícius Raposo Ribeiro<br>\n Lucas Peres Oliveira<br>\n Romina Batista<br>\n Marcos Paulo Alves de Sousa\n\n\n ## Contact\n\nDr. Marcos Paulo Alves de Sousa (Project leader)\n\n_Email: **msousa@museu-goeldi.br**_<br>\n_Laboratório de Biologia Molecular-LBM_<br>\n_Grupo de pesquisa em Bioinformática e Informática para Biodiversidade (BioInfo)_<br>\n_Museu Paraense Emílio Goeldi_<br>\n_Av. Perimetral 1901. CEP 66077- 530. Belém, Pará, Brazil._\n',
    'author': 'Caio Raposo',
    'author_email': 'caioraposo@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://uceasy.github.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
