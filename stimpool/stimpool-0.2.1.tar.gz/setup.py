# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['stimpool']

package_data = \
{'': ['*'], 'stimpool': ['words/*', 'words/META-INF/*']}

install_requires = \
['click>=7.1.2,<8.0.0', 'pandas', 'sphinx-markdown-tables>=0.0.15,<0.0.16']

entry_points = \
{'console_scripts': ['stimpool = stimpool.cli:main']}

setup_kwargs = {
    'name': 'stimpool',
    'version': '0.2.1',
    'description': 'Create stimuli pools for psychological research',
    'long_description': '\n# stimpool\n\n\n[![PyPI - Version](https://img.shields.io/pypi/v/stimpool.svg)](https://pypi.python.org/pypi/stimpool)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stimpool.svg)](https://pypi.python.org/pypi/stimpool)\n![GitHub](https://img.shields.io/github/license/mario-bermonti/stimpool)\n[![Tests](https://github.com/mario-bermonti/stimpool/workflows/tests/badge.svg)](https://github.com/mario-bermonti/stimpool/actions?workflow=tests)\n[![codecov](https://codecov.io/gh/mario-bermonti/stimpool/branch/master/graph/badge.svg?token=GGADPVQ5G2)](https://codecov.io/gh/mario-bermonti/stimpool)\n[![Read the Docs](https://readthedocs.org/projects/stimpool/badge/)](https://stimpool.readthedocs.io/)\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n\nEasily create stimuli pools for cognitive, learning, and psycholinguistics research\n\n\n* GitHub repo: <https://github.com/mario-bermonti/stimpool.git>\n* Documentation: <https://stimpool.readthedocs.io/>\n* Free software: BSD-3 Clause\n\n\n## Features\n\n* Easily create Spanish word pools for research\n* Specify the characteristics that meet your needs\n* Provide your own word pool or use the default one\n* Get the cleaned pool or save it to a file\n\n## Getting Started\n### Installation\n`pip install stimpool`\n\n### Usage\n```python\nfrom stimpool import WordPool\nwords = ["gato", "canción", "oso", "otorrinolaringólogo"]\nword_pool = WordPool(words)\nword_pool.select_words_without_accented_characters()\nprint(word_pool.words)\n```\n\nCheck [the documentation][project_docs] for more details.\n\n## Contributing to this project\n  All contributions are welcome!\n\n  Will find a detailed description of all the ways you can contribute to stimpool in\n  [the contributing guide][contributing_guide].\n\n  This is a beginner-friendly project so don\'t hesitate to ask any questions or get in touch\n  with the project\'s maintainers.\n\n  Please review the [project\'s code of conduct][code_conduct] before making\n  any contributions.\n\n## Author\n  This project was developed by Mario E. Bermonti-Pérez as part of\n  his academic research. Feel free to contact me at\n  [mbermonti@psm.edu](mailto:mbermonti@psm.edu)  or\n  [mbermonti1132@gmail.com](mailto:mbermonti1132@gmail.com)\n\n## Credits\nThis package was created with [Cookiecutter][cookiecutter] and the [fedejaure/cookiecutter-modern-pypackage][cookiecutter-modern-pypackage] project template.\n\n[cookiecutter]: https://github.com/cookiecutter/cookiecutter\n[cookiecutter-modern-pypackage]: https://github.com/fedejaure/cookiecutter-modern-pypackage\n[project_docs]: https://stimpool.readthedocs.io/\n[code_conduct]: ./CODE_OF_CONDUCT.md\n[contributing_guide]: ./contributing.md\n',
    'author': 'Mario E. Bermonti Pérez',
    'author_email': 'mbermonti1132@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mario-bermonti/stimpool',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<3.10',
}


setup(**setup_kwargs)
