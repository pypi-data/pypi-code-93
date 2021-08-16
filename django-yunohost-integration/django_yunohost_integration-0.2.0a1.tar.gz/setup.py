# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_yunohost_integration',
 'django_yunohost_integration.management',
 'django_yunohost_integration.management.commands',
 'django_yunohost_integration.sso_auth']

package_data = \
{'': ['*']}

install_requires = \
['django']

extras_require = \
{'ynh': ['gunicorn', 'psycopg2', 'django-redis', 'django-axes']}

entry_points = \
{'console_scripts': ['devshell = '
                     'django_yunohost_integration.dev_shell:devshell_cmdloop']}

setup_kwargs = {
    'name': 'django-yunohost-integration',
    'version': '0.2.0a1',
    'description': 'Glue code to package django projects as yunohost apps.',
    'long_description': '# django_yunohost_integration\n\nPython package [django_yunohost_integration](https://pypi.org/project/django_yunohost_integration/) with helpers for integrate a Django project as YunoHost package.\n\nA example usage of this package is here:\n\n* https://github.com/YunoHost-Apps/django_example_ynh\n\nPull requests welcome ;)\n\n\nThese projects used `django_yunohost_integration`:\n\n* https://github.com/YunoHost-Apps/pyinventory_ynh\n* https://github.com/YunoHost-Apps/django-for-runners_ynh\n\n\n## Features\n\n* SSOwat integration (see below)\n* Helper to create first super user for `scripts/install`\n* Run Django development server with a local generated YunoHost package installation (called `local_test`)\n* Run `pytest` against `local_test` "installation"\n\n\n### SSO authentication\n\n[SSOwat](https://github.com/YunoHost/SSOwat) is fully supported:\n\n* First user (`$YNH_APP_ARG_ADMIN`) will be created as Django\'s super user\n* All new users will be created as normal users\n* Login via SSO is fully supported\n* User Email, First / Last name will be updated from SSO data\n\n\n### usage\n\nTo create/update the first user in `install`/`upgrade`, e.g.:\n\n```bash\n./manage.py create_superuser --username="$admin" --email="$admin_mail"\n```\nThis Create/update Django superuser and set a unusable password.\nA password is not needed, because auth done via SSOwat ;)\n\nMain parts in `settings.py`:\n```python\nfrom django_yunohost_integration.secret_key import get_or_create_secret as __get_or_create_secret\n\n# Function that will be called to finalize a user profile:\nYNH_SETUP_USER = \'setup_user.setup_project_user\'\n\nSECRET_KEY = __get_or_create_secret(FINAL_HOME_PATH / \'secret.txt\')  # /opt/yunohost/$app/secret.txt\n\nINSTALLED_APPS = [\n    #...\n    \'django_yunohost_integration\',\n    #...\n]\n\nMIDDLEWARE = [\n    #... after AuthenticationMiddleware ...\n    #\n    # login a user via HTTP_REMOTE_USER header from SSOwat:\n    \'django_yunohost_integration.sso_auth.auth_middleware.SSOwatRemoteUserMiddleware\',\n    #...\n]\n\n# Keep ModelBackend around for per-user permissions and superuser\nAUTHENTICATION_BACKENDS = (\n    \'axes.backends.AxesBackend\',  # AxesBackend should be the first backend!\n    #\n    # Authenticate via SSO and nginx \'HTTP_REMOTE_USER\' header:\n    \'django_yunohost_integration.sso_auth.auth_backend.SSOwatUserBackend\',\n    #\n    # Fallback to normal Django model backend:\n    \'django.contrib.auth.backends.ModelBackend\',\n)\n\nLOGIN_REDIRECT_URL = None\nLOGIN_URL = \'/yunohost/sso/\'\nLOGOUT_REDIRECT_URL = \'/yunohost/sso/\'\n```\n\n\n## local test\n\nFor quicker developing of django_yunohost_integration in the context of YunoHost app,\nit\'s possible to run the Django developer server with the settings\nand urls made for YunoHost installation.\n\ne.g.:\n```bash\n~$ git clone https://github.com/jedie/django_yunohost_integration.git\n~$ cd django_yunohost_integration/\n~/django_yunohost_integration$ ./devshell.py\n\n+ .venv/bin/python .venv/bin/devshell\n\n\n\nDeveloper shell - django_yunohost_integration - v0.2.0.alpha1\n\n\nDocumented commands (use \'help -v\' for verbose/\'help <topic>\' for details):\n\ndev-shell commands\n==================\nfix_code_style  linting  list_venv_packages  publish  pytest  update\n\n\nDjango-YunoHost-Integration commands\n====================================\nlocal_test\n\nUncategorized\n=============\nalias  help     macro  run_pyscript  set    shortcuts\nedit   history  quit   run_script    shell\n\n\n(django_yunohost_integration)\n```\n\nFor quicker developing of django_yunohost_integration in the context of YunoHost app,\nit\'s possible to run the Django developer server with the settings\nand urls made for YunoHost installation.\n\ne.g.:\n```bash\n~/django_yunohost_integration$ ./devshell.py\n(django_yunohost_integration) local_test\n```\n\n* SQlite database will be used\n* A super user with username `test` and password `test` is created\n* The page is available under `http://127.0.0.1:8000/app_path/`\n\n\n## history\n\n* [compare v0.1.5...master](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.5...master) **dev**\n  * tbc\n* v0.2.0.alpha1 **dev**\n  * rename/split `django_ynh` into:\n    * `django_yunohost_integration` - Python package with the glue code to integrate a Django project with YunoHost\n    * `django_example_ynh` - Demo YunoHost App to demonstrate the integration of a Django project under YunoHost\n* [v0.1.5 - 19.01.2021](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.4...v0.1.5)\n  * Make some deps `gunicorn`, `psycopg2-binary`, `django-redis`, `django-axes` optional\n* [v0.1.4 - 08.01.2021](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.3...v0.1.4)\n  * Bugfix [CSRF verification failed on POST requests #7](https://github.com/YunoHost-Apps/django_yunohost_integration/issues/7)\n* [v0.1.3 - 08.01.2021](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.2...v0.1.3)\n  * set "DEBUG = True" in local_test (so static files are served and auth works)\n  * Bugfixes and cleanups\n* [v0.1.2 - 29.12.2020](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.1...v0.1.2)\n  * Bugfixes\n* [v0.1.1 - 29.12.2020](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/v0.1.0...v0.1.1)\n  * Refactor "create_superuser" to a manage command, useable via "django_yunohost_integration" in `INSTALLED_APPS`\n  * Generate "conf/requirements.txt" and use this file for install\n  * rename own settings and urls (in `/conf/`)\n* [v0.1.0 - 28.12.2020](https://github.com/YunoHost-Apps/django_yunohost_integration/compare/f578f14...v0.1.0)\n  * first working state\n* [23.12.2020](https://github.com/YunoHost-Apps/django_yunohost_integration/commit/f578f144a3a6d11d7044597c37d550d29c247773)\n  * init the project\n\n\n## Links\n\n* Report a bug about this package: https://github.com/YunoHost-Apps/django_yunohost_integration\n* YunoHost website: https://yunohost.org/\n* PyPi package: https://pypi.org/project/django_yunohost_integration/\n\n\n\n',
    'author': 'JensDiemer',
    'author_email': 'git@jensdiemer.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jedie/django_yunohost_integration',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0.0',
}


setup(**setup_kwargs)
