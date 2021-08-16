# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['multilint']
install_requires = \
['autoflake>=1.4,<2.0',
 'black>=21.5b0,<22.0',
 'isort>=5.8.0,<6.0.0',
 'mypy>=0.812,<0.813',
 'pydocstyle>=6.0.0,<7.0.0',
 'pylint>=2.8.2,<3.0.0',
 'pyupgrade>=2.14.0,<3.0.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['multilint = multilint:main']}

setup_kwargs = {
    'name': 'pymultilint',
    'version': '0.4.0',
    'description': 'Utility tying multiple code quality tools together',
    'long_description': '# Multilint (for Python)\n\n[![Actions Test Workflow Widget](https://github.com/gkze/multilint/workflows/ci/badge.svg)](https://github.com/gkze/multilint/actions?query=workflow%3Aci)\n[![PyPI Version](https://img.shields.io/pypi/v/pymultilint)](https://pypi.org/project/pymultilint/)\n[![Pdoc Documentation](https://img.shields.io/badge/pdoc-docs-green)](https://gkze.github.io/multilint/multilint.html)\n\nA utility tying together multiple linting and other code quality tools\n\n## Intro\n\nMultilint allows running several code quality tools under the same interface.\nThis is convenient as it saves time on writing multiple linter / formatter /\nchecker invocations every time in a project.\n\n## Installation\n\nSince there is an existing project called\n[`multilint`](https://pypi.org/project/multilint/), this Multilint can be\ninstalled as `pymultilint`:\n\n```bash\n$ pip3 install multilint\n```\n\n## Usage\n\nMultilint exposes a CLI entry point:\n\n```bash\n$ multilint [paths ...]\n```\n\nIt can optionally take a set of starting paths. There are no CLI options,\nas Multilint strives to have all of its configuration codified (see\n[Configurability](#configurability)).\n\nAlternatively, Multilint is also usable via its API - either the\n[`main`](multilint.py#L526) method, or the\n[`Multilint`](multilint.py#L447) class\n\n## Supported Tools\n\nCurrently, Multilint integrates the following code quality tools:\n\n* [Autoflake](https://github.com/myint/autoflake) - removes unused imports and\n  unused variables as identified by [Pyflakes](https://github.com/PyCQA/pyflakes)\n* [Isort](https://pycqa.github.io/isort/) - sorts imports according to specified\n  orders\n* [Black](https://black.readthedocs.io/en/stable/) - the self-proclaimed\n  "uncompromising code formatter" - formats Python source with an opinionated\n  style\n* [Mypy](http://mypy-lang.org) - static type checker for Python\n* [Pylint](https://www.pylint.org) - general best practices linter\n* [Pydocstyle](http://www.pydocstyle.org/en/stable/) - in-source documentation\n  best practices linter\n* [Pyupgrade](https://github.com/asottile/pyupgrade) - upgrades Python syntax to\n  the latest for the specified version\n\n## Configurability\n\nAdditionally, for tools that do not currently support configuration via\n`pyproject.toml`([PEP-621](https://www.python.org/dev/peps/pep-0621/)),\nMultilint exposes a configuration interface for them. This allows for\ncentralized codification of configuration of all code quality tools being used\nin a project.\n\nExample relevant sections from a `pyproject.toml`:\n\n```toml\n[tool.autoflake]\nrecursive = true\nin_place = true\nignore_init_module_imports = true\nremove_all_unused_imports = true\nremove_unused_variables = true\nverbose = true\nsrcs_paths = ["somepackage"]\n\n[tool.mypy]\nsrc_paths = ["someotherpackage"]\n\n[tool.multilint]\ntool_order = [\n  "autoflake",\n  "isort",\n  "pyupgrade",\n  "black",\n  "mypy",\n  "pylint",\n  "pydocstyle"\n]\nsrc_paths = ["."]\n```\n\nAt the time of writing of this README (2020-01-31), neither\n[Autoflake](https://github.com/myint/autoflake/issues/59) nor\n[Mypy](https://github.com/python/mypy/issues/5205https://github.com/python/mypy/issues/5205)\nsupport configuration via `pyproject.toml`. While support for each may or may\nnot be added at some point in the future, with multilint configuring these tools\nis possible **today**.\n\nCurrently, the only two supported configuration option for Multilint are:\n\n* `tool_order`, which defines the execution order of supported tools, and\n* `src_paths`, which specifies the source paths (can be files and directories)\n  for Multilint to operate on.\n\nEach integrated tool additionally supports `src_dirs` as an override, in case\nit is desired to target a specific tool at a different set of files\n/ directories.\n\n## Extending Multilint\n\nSupport for more tools may be added by subclassing the\n[`ToolRunner`](multilint.py#L127) class and overriding the\n[`.run(...)`](multilint.py#L159) method.\n\nThere are some utilities provided, such as:\n\n* A logger that masquerades as a TextIO object to allow capturing tool output\n  from within and wrapping it with preferred logging\n* A dictionary for tool configuration that is automatically available in the\n  `ToolRunner` class, as long as the tool is registered in\n  * The [`Tool`](multilint.py#L47) enum,\n  * The [`TOOL_RUNNERS`](multilint.py#L446) mapping, and declared\n  * The [`DEFAULT_TOOL_ORDER`](multilint.py#L465) class variable of `Multilint`.\n\nDocumentation about adding support for more tools to Multilint may be added in\nthe future.\n',
    'author': 'George Kontridze',
    'author_email': 'george.kontridze@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gkze/multilint',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
