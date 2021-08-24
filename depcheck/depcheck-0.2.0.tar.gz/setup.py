# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['depcheck']

package_data = \
{'': ['*']}

install_requires = \
['pydeps>=1.9.13,<2.0.0']

entry_points = \
{'console_scripts': ['depcheck = depcheck.main:main']}

setup_kwargs = {
    'name': 'depcheck',
    'version': '0.2.0',
    'description': 'Depcheck is a tool to check package dependencies between predefined layers to make sure that the application always complies with the architecture you defined. It helps you enforcing some constraints and creating a decoupled applications.',
    'long_description': "![Depcheck: Dependency Checker](https://images2.imgbox.com/da/85/J5OEzbAH_o.jpg)\n\nDepcheck is a tool to check package-dependencies between predefined layers. \nIn the configuration file(`.depcheck.yml`) located in the project root, \nwhich packages belong to which layers and allowed dependencies between \nlayers are configurable. In this way, you can enforce constraints and make sure to have decoupled architecture.\n\n## Install\nInstall from [Pypi][pypi-link] via `pip install depcheck`\n    \n## Usage\nLet's say you have a project with the directory structure below:\n```text\nexample\n    root\n        foo\n        bar\n        main.py\n        __init__.py\n    README.md\n    .gitignore\n    .depcheck.yml\n```\nNote: Package directories should contain **\\_\\_init\\_\\_.py** to be recognized as a package.\n- Navigate to the `exampe` then run `depcheck` for your project:\n    ```shell\n    depcheck root\n    ```\n- As you can see in the directory structure above, we have `.depcheck.yml` \n  configuration file in the project directory. If you would like to change \n  the path of the configuration file, use `-f` or `--file` argument:\n    ```shell\n    depcheck root -f /path/to/your/custom/depcheck.yml\n    ```\n\n## Contributing\nAll contributions are welcomed! See our [CONTRIBUTING.md][contribution] document.\n\n\n<!-- Links -->\n[hexagonal-architecture]: https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)\n[upgrade-python-version]: ./docs/upgrade-python-version.md\n[update-project-dependencies]: ./docs/upgrade-python-version.md\n[pypi-link]: https://pypi.org/project/depcheck/\n[contribution]: ./CONTRIBUTING.md\n",
    'author': 'FlixMobility Tech',
    'author_email': 'open-source@flixbus.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/flix-tech/depcheck',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
