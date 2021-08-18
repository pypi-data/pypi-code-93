# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['depcheck']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0', 'pydeps>=1.9.13,<2.0.0']

entry_points = \
{'console_scripts': ['depcheck = depcheck.main:main']}

setup_kwargs = {
    'name': 'depcheck',
    'version': '0.1.1',
    'description': 'Depcheck is a tool to check package dependencies between predefined layers to make sure that the application always complies with the Hexagonal Architecture principle of creating loosely coupled application components.',
    'long_description': "![Depcheck: Dependency Checker](/docs/.img/depcheck_logo.jpg)\n\nDepcheck is a tool to check package-dependencies between predefined layers. \nIn the configuration file(`.depcheck.yml`) located in the project root, \nwhich packages belong to which layers and allowed dependencies between \nlayers are configurable. In this way, you can make sure that the application \nalways complies with the [Hexagonal Architecture][hexagonal-architecture] \nprinciple of creating loosely coupled application components.\n\n## Install\nInstall from [Pypi][pypi-link] via `pip install depcheck`\n    \n## Usage\nLet's say you have a project with the directory structure below:\n```text\nproject_directory\n    root_package\n        package-1\n        package-2\n        main.py\n    README.md\n    .gitignore\n    .depcheck.yml\n```\n- Navigate to the `project_directory` then run `depcheck` for your project:\n    ```shell\n    depcheck root_package\n    ```\n- As you can see in the directory structure above, we have `.depcheck.yml` \n  configuration file in the project directory. If you would like to change \n  the path of the configuration file, use `-f` or `--file` argument:\n    ```shell\n    depcheck root_package -f config/customized_depcheck.yml\n    ```\n\n## Contributing\nAll contributions are welcomed! Start by searching through the [issues][issues] and \n[pull requests][pull-requests] to see whether someone else has raised a similar idea or question.\nIf you don't see your idea listed, open a pull request.\n\n## Maintenance Work\n- [Upgrade project's Python version][upgrade-python-version]\n- [Update project dependencies][update-project-dependencies]\n\n\n<!-- Links -->\n[hexagonal-architecture]: https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)\n[upgrade-python-version]: ./docs/upgrade-python-version.md\n[update-project-dependencies]: ./docs/upgrade-python-version.md\n[pypi-link]: https://pypi.org/project/depcheck/\n[issues]: https://github.com/flix-tech/depcheck/issues\n[pull-requests]: https://github.com/flix-tech/depcheck/pulls\n",
    'author': 'FlixMobility Tech',
    'author_email': 'open-source@flixbus.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/flix-tech/depcheck',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9.6,<4.0.0',
}


setup(**setup_kwargs)
