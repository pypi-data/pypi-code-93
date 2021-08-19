# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xontrib', 'xontrib_powerline3']

package_data = \
{'': ['*']}

install_requires = \
['tomlkit', 'xonsh>=0.9.20']

setup_kwargs = {
    'name': 'xontrib-powerline3',
    'version': '0.3.5',
    'description': 'Yet another powerline theme for xonsh with async prompt support.',
    'long_description': '# Powerline3\nYet another powerline theme for xonsh with async prompt support. \n\n# Note: \nThis depends on xonsh\'s unreleased version (master branch will work. or in future >0.9.24)\n\n## Why another one?\n\n- It uses `$PROMPT_FIELDS` and no need to have a separate functions and renderer. \n  Since the addition of `$PROMPT_TOKENS_FORMATTER` it is possible to use the existing \n  set of functions to emulate powerline theme for xonsh prompts.\n- Async prompt mode works as well. \n\n## Installation\n\nTo install use pip:\n\n``` bash\nxpip install xontrib-powerline3\n# or: xpip install -U git+https://github.com/jnoortheen/xontrib-powerline3\n```\n\n## Usage\n\n``` bash\nxontrib load powerline3\n\n# these are the default colors and they are configurable.\n$PROMPT_FIELD_COLORS = {\n    "cwd": ("WHITE", "CYAN"),\n    "gitstatus": ("WHITE", "BLACK"),\n    "ret_code": ("WHITE", "RED"),\n    "full_env_name": ("white", "green"),\n    "hostname": ("white", BLUE),\n    "localtime": ("#DAF7A6", "black"),\n}\n\n# choose the powerline glyph used\n$POWERLINE_MODE = "powerline" # if not set then it will choose random\n  # available modes: round/down/up/flame/squares/ruiny/lego\n\n# define the prompts using the format style and you are good to go\n$PROMPT = "".join(\n    [\n        "{vte_new_tab_cwd}",\n        "{cwd:{}}",\n        "{gitstatus:\ue0a0{}}",\n        "{ret_code}",\n        "{background_jobs}",\n        os.linesep,\n        "{full_env_name: 🐍{}}",\n        "$",\n    ]\n)\n$RIGHT_PROMPT = "".join(\n    (\n        "{long_cmd_duration: ⌛{}}",\n        "{user: 🤖{}}",\n        "{hostname: 🖥{}}",\n        "{localtime: 🕰{}}",\n    )\n)\n```\n\n## Extra PROMPT_FIELDS\n\n### 1. `full_env_name`\n\n- When the `env_name` is \n  - `.venv` show the name of the parent folder\n  - contains `-py3.*` (when it is poetry created) shows the project name part alone\n  \n### 2. `background_jobs`\n- show number of running background jobs\n\n### 3. py_pkg_info\n- show python package `name-version` if current directory has poetry-pyproject.toml\n\n## Examples\n\n![screenshot.png](docs/screenshot.png)\n\n## Credits\n\nThis package was created with [xontrib cookiecutter template](https://github.com/jnoortheen/xontrib-cookiecutter).\n- https://www.nerdfonts.com/cheat-sheet?set=nf-ple-\n- https://github.com/romkatv/powerlevel10k#meslo-nerd-font-patched-for-powerlevel10k\n\n## Similar Projects\n- https://github.com/vaaaaanquish/xontrib-powerline2\n- https://github.com/santagada/xontrib-powerline\n',
    'author': 'Noortheen Raja NJ',
    'author_email': 'jnoortheen@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jnoortheen/xontrib-powerline3',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
