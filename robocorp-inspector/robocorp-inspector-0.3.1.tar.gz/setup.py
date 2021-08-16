# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['inspector', 'inspector.windows']

package_data = \
{'': ['*']}

install_requires = \
['mss>=6.1.0,<7.0.0',
 'pywebview>=3.5,<4.0',
 'requests>=2.25.1,<3.0.0',
 'rpaframework-core>=6.0.0,<7.0.0',
 'rpaframework-recognition>=0.7.2,<0.8.0']

entry_points = \
{'console_scripts': ['inspector = inspector.cli:run']}

setup_kwargs = {
    'name': 'robocorp-inspector',
    'version': '0.3.1',
    'description': 'Robocorp Inspector',
    'long_description': '# Robocorp Inspector\n\nRobocorp Inspector is a tool for exploring various user interfaces\nand developing ways to target elements within them. An expression\nthat can target specific UI elemements is called a _locator_, and\nthese locators can be used to automate applications typically\nused by humans.\n\n## Development\n\nThe project uses `invoke` for overall project management, `poetry` for\npython dependencies and environments, and `yarn` for Javascript dependencies\nand building.\n\nBoth `invoke` and `poetry` should be installed via pip: `pip install poetry invoke`\n\n- To see all possible tasks: `invoke --list`\n- To run the project: `invoke run `\n\nAll source code is hosted on [GitHub](https://github.com/robocorp/inspector/).\n\n## Usage\n\nRobocorp Inspector is distributed as a Python package with all front-end\ncomponents compiled and included statically.\n\nIf the package (and all required dependencies) is installed manually,\nit can be run with the command: `inspector`.\n\nPackages are automatically uploaded to [devpi](https://devpi.robocorp.cloud) by [Github Actions](https://github.com/robocorp/inspector/actions).\nThe workflow also updates a robot in [Robocorp Cloud](https://cloud.robocorp.com/orgrobocorp/robocorp/packages/4686),\nwhich can be used via [Robocorp Assistant](https://cloud.robocorp.com/orgrobocorp/robocorp/assistants/7236d993-f0b6-4590-a3a3-dc2ec4c89578).\n\n---\n\n<p align="center">\n  <img height="100" src="https://cdn.robocorp.com/brand/Logo/Dark%20logo%20transparent%20with%20buffer%20space/Dark%20logo%20transparent%20with%20buffer%20space.svg">\n</p>\n',
    'author': 'Ossi Rajuvaara',
    'author_email': 'ossi@rajuvaara.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/robocorp/inspector',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
