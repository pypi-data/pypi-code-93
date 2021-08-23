# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastapi_template',
 'fastapi_template.template.hooks',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.db',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.db.dao',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.db.migrations',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.db.migrations.versions',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.db.models',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.services.redis',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.tests',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.web',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.web.api',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.web.api.dummy',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.web.api.echo',
 'fastapi_template.template.{{cookiecutter.project_name}}.{{cookiecutter.project_name}}.web.api.redis']

package_data = \
{'': ['*'],
 'fastapi_template': ['template/*',
                      'template/{{cookiecutter.project_name}}/*',
                      'template/{{cookiecutter.project_name}}/.github/workflows/*',
                      'template/{{cookiecutter.project_name}}/deploy/*',
                      'template/{{cookiecutter.project_name}}/deploy/kube/*']}

install_requires = \
['cookiecutter>=1.7.3,<2.0.0',
 'pre-commit>=2.14.0,<3.0.0',
 'prompt-toolkit>=3.0.19,<4.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'pygit2>=1.6.0,<2.0.0',
 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['fastapi_template = fastapi_template.__main__:main']}

setup_kwargs = {
    'name': 'fastapi-template',
    'version': '2.1.1',
    'description': 'Feature-rich robust FastAPI template',
    'long_description': '![python version](https://img.shields.io/pypi/pyversions/fastapi_template?style=flat-square) ![Build status](https://img.shields.io/github/workflow/status/s3rius/FastAPI-template/Release%20python%20package?style=flat-square) [![version](https://img.shields.io/pypi/v/fastapi_template?style=flat-square)](https://pypi.org/project/fastapi-template/)\n\n<div align="center">\n<img src="https://raw.githubusercontent.com/s3rius/FastAPI-template/master/images/logo.png" width=700>\n<div><i>Fast and flexible general-purpose template for your API.</i></div>\n</div>\n\n<div align="center">\n<img src="https://raw.githubusercontent.com/s3rius/FastAPI-template/master/images/ui-example.png" width=700>\n<div><i>With text user interface.</i></div>\n</div>\n\n## Usage\n\n⚠️ [Git](https://git-scm.com/downloads), [Python](https://www.python.org/) and [Poetry](https://python-poetry.org/) must be installed and accessible ⚠️\n\n```bash\npython3 -m pip install fastapi_template\npython3 -m fastapi_template\n# or fastapi_template\n# Answer all the questions\n# 🍪 Enjoy your new project 🍪\ncd new_project\ndocker-compose -f deploy/docker-compose.yml --project-directory . up --build\n```\n\nIf you want to install in from sources then try this:\n```shell\npython3 -m pip install poetry\npython3 -m pip install .\npython3 -m fastapi_template\n```\n\n## Features\n\nTemplate is made with SQLAlchemy14 and uses sqlalchemy orm and sessions,\ninstead of raw drivers.\n\nIt has minimum to start new excellent project.\n\nGenerator features:\n- Different databases to choose from.\n- Alembic integration;\n- redis support;\n- different CI\\CD templates;\n- Kubernetes config.\n\nThis project can handle arguments passed through command line.\n\n```shell\n$ python -m fastapi_template --help\n\nusage: FastAPI template [-h] [--name PROJECT_NAME]\n                        [--description PROJECT_DESCRIPTION]\n                        [--db {DatabaseType.none,DatabaseType.sqlite,DatabaseType.mysql,DatabaseType.postgresql}]\n                        [--ci {CIType.none,CIType.gitlab_ci,CIType.github}]\n                        [--redis] [--alembic] [--kube] [--force]\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --name PROJECT_NAME   Name of your awesome project\n  --description PROJECT_DESCRIPTION\n                        Project description\n  --db {DatabaseType.none,DatabaseType.sqlite,DatabaseType.mysql,DatabaseType.postgresql}\n                        Database\n  --ci {CIType.none,CIType.gitlab_ci,CIType.github}\n                        Choose CI support\n  --redis               Add redis support\n  --alembic             Add alembic support\n  --kube                Add kubernetes configs\n  --force               Owerrite directory if it exists\n```\n',
    'author': 'Pavel Kirilin',
    'author_email': 'win10@list.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/s3rius/FastAPI-template',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
