# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['docker_snapshot', 'docker_snapshot.images']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'click-aliases>=1.0.1,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'docker>=5.0.0,<6.0.0',
 'hruid>=0.0.3,<0.0.4',
 'rich>=10.7.0,<11.0.0']

entry_points = \
{'console_scripts': ['ds = docker_snapshot.main:execute_cli']}

setup_kwargs = {
    'name': 'docker-snapshot',
    'version': '1.0.4',
    'description': '`ds` is a development utility for managing snapshots inside a docker container.',
    'long_description': '# ds - docker snapshot\n\n`ds` is a development utility for managing snapshots inside a docker container.\n\nPersonally I use it to quickly save the state of my development database, try out something that mutates the state - a data migration or user interaction - and return to the initial state. Often repeatedly, because trial and error is essential. You can probably use it on any sort of stored data, probably. \n\nNote: This repository is still a work in progress.\n\n## Installing\n```bash\n# Note: excutable will be called `ds`\npip install docker-snapshot\n```\n\nShell completion:\n```bash\n# For Bash, add this to ~/.bashrc:\neval "$(_DS_COMPLETE=source_bash ds)"\n\n# For Zsh, add this to ~/.zshrc:\neval "$(_DS_COMPLETE=source_zsh ds)"\n```\n\n\n## Usage\n\nCreate a snapshot\n```bash\nds create name-goes-here\n# or auto-generate a name\nds create \n```\n\nRestore a snapshot\n```bash\nds restore name-goes-here\n# or restore the latest snapshot\nds restore\n```\n\nList snapshots\n```bash\nds ls\n```\n\nDelete snapshots\n```bash\nds delete name-goes-here\n```\n\n## Example project setup\nIn this example we use `ds` to create and restore database snapshots in our development environment. The projects `docker-compose.yml` file could look something like this:\n```\nversion: "3.8"\nservices:\n  db:\n    container_name: db\n    restart: always\n    image: postgres:13\n    env_file: .env\n    ports:\n      - 5432:5432\n    volumes:\n      - db-volume:/var/lib/postgresql/data\n  ...\n```\n\n1) Browse to your project root\n```bash\ncd code/your-awesome-project\n```\n\n2) Create `ds.yaml` template file\n```bash\nds init\n```\n\n3) Edit your `ds.yaml`\n```yaml\n# The target container\ncontainer_name: "db"\n\n# The directory inside said container that you want to snapshot\ndirectory: "/var/lib/postgresql/data"\n\n# Identifier to separate projects, this allows you:\n# - To have multiple projects with the same container name\n# - To have multiple setups (ie. docker-compose / kind) for the same project\nnamespace: "your-awesome-project"\n```\n',
    'author': 'occamz',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/occamz/ds',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
