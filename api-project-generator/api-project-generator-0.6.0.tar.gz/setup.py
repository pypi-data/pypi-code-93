# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['api_project_generator',
 'api_project_generator.commands',
 'api_project_generator.helpers',
 'api_project_generator.models']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.18,<4.0.0', 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['api-project = api_project_generator.main:app']}

setup_kwargs = {
    'name': 'api-project-generator',
    'version': '0.6.0',
    'description': '',
    'long_description': '# API Project Generator\n\nSimple API Structure Generator using tecnologies:\n\n- FastAPI\n- SQLAlchemy\n- aiohttp\n- aiomysql or asyncpg\n\n## Commands\n\n- `create:api`: Creates the project structure and base classes\n\n  > Optional `--code` option auto opens code through a `code project_folder_name` command.\n  > Optional `--db-type` option allows to select database type from "postgres" or "mysql". (default: mysql)\n\n  ```bash\n  api-project create\n  ```\n\n- `create:table`: Creates a new table in file in {project_name}/database/tables/{table_module}/{table_file}.py\n\n  ```bash\n  api-project create:table [table_module] [table_name]\n  ```\n\n- `create:dto`: Creates a new DTO file in {project_name}/dtos/{dtos_module}/{dto_name}.py\n\n  ```bash\n  api-project create:dto [dtos_module] [dto_name]\n  ```\n\n- `create:enum`: Creates a new Enum file in {project_name}/dtos/enums/{enum_name}.py\n\n  > The `auto-opts` option in the command can be repeated and will be used as the enum field\n\n  ```bash\n  api-project create:enum [enum_name] --auto-opts [opt_name]\n  ```\n\n- `create:entity`: Creates dtos, routes, repository and table for desired entity\n\n  > Optional `--sync` option allow to toggle between async repositories and routes or synchronous ones.\n\n  ```bash\n  api-project create:entity [entity_module] [entity_name]\n  ```\n\n\n### Observations\n\n> All filenames and foldernames are\n>\n> normalized automatically to snake_case.\n',
    'author': 'Gustavo Correa',
    'author_email': 'self.gustavocorrea@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
