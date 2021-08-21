# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_exec_plugin']

package_data = \
{'': ['*']}

install_requires = \
['poetry>=1.2.0.a2,<2.0.0',
 'simple-chalk>=0.1.0,<0.2.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'poetry.application.plugin': ['exec = poetry_exec_plugin.plugin:ExecPlugin']}

setup_kwargs = {
    'name': 'poetry-exec-plugin',
    'version': '0.2.1',
    'description': 'A plugin for poetry that allows you to execute scripts defined in your pyproject.toml, just like you can in npm or pipenv.',
    'long_description': '# poetry-exec-plugin\n\nA plugin for poetry that allows you to execute scripts defined in your pyproject.toml, just like you can in npm or pipenv\n\n## Installation\n\nInstallation requires poetry 1.2.0+. To install this plugin run:\n\n`pip install poetry-exec-plugin`\n\nFor other methods of installing plugins see the [poetry documentation](https://python-poetry.org/docs/master/plugins/#the-plugin-add-command).\n\n## Usage\n\nTo use this plugin, first define the scripts that you wish to be able to execute in your `pyproject.toml` file under a section called `tool.poetry-exec-plugin.commands`. For example:\n\n```toml\n[tool.poetry-exec-plugin.commands]\nhello-world = "TEXT=hello-world; echo $TEXT"\nlint = "flake8"\n```\n\nThis will define a script that you can then execute with the `poetry exec <script>` command. This will execute your script inside of the environment that poetry creates for you, allowing you to access the dependencies installed for your project. For example:\n\n```bash\n$ poetry exec hello-world\nhello-world\n\n$ poetry exec lint\n./my_file.py:29:25: E222 multiple spaces after operator\n```\n\nAnything that you append to your exec command will be appended to the script. You can use this to pass extra flags and arguments to the commands in your scripts. For example:\n\n```bash\n$ poetry exec hello-world one two three\nhello-world one two three\n\n$ poetry exec lint --version\n3.9.2 (mccabe: 0.6.1, pycodestyle: 2.7.0, pyflakes: 2.3.1) CPython 3.9.0 on Darwin\n```\n',
    'author': 'keattang',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/keattang/poetry-exec-plugin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
