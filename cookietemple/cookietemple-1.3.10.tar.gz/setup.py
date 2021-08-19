# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cookietemple',
 'cookietemple.bump_version',
 'cookietemple.common',
 'cookietemple.config',
 'cookietemple.create',
 'cookietemple.create.domains',
 'cookietemple.create.templates',
 'cookietemple.create.templates.cli.cli_python.{{ '
 'cookiecutter.project_slug_no_hyphen }}',
 'cookietemple.create.templates.cli.cli_python.{{ '
 'cookiecutter.project_slug_no_hyphen }}.tests',
 'cookietemple.create.templates.cli.cli_python.{{ '
 'cookiecutter.project_slug_no_hyphen }}.{{ '
 'cookiecutter.project_slug_no_hyphen }}',
 'cookietemple.create.templates.common_files.{{cookiecutter.commonName}}.docs',
 'cookietemple.create.templates.web.website_python.flask.{{ '
 'cookiecutter.project_slug_no_hyphen }}',
 'cookietemple.create.templates.web.website_python.flask.{{ '
 'cookiecutter.project_slug_no_hyphen }}.tests',
 'cookietemple.create.templates.web.website_python.flask.{{ '
 'cookiecutter.project_slug_no_hyphen }}.{{ '
 'cookiecutter.project_slug_no_hyphen }}',
 'cookietemple.create.templates.web.website_python.flask.{{ '
 'cookiecutter.project_slug_no_hyphen }}.{{ '
 'cookiecutter.project_slug_no_hyphen }}.auth',
 'cookietemple.create.templates.web.website_python.flask.{{ '
 'cookiecutter.project_slug_no_hyphen }}.{{ '
 'cookiecutter.project_slug_no_hyphen }}.auth.forms',
 'cookietemple.create.templates.web.website_python.flask.{{ '
 'cookiecutter.project_slug_no_hyphen }}.{{ '
 'cookiecutter.project_slug_no_hyphen }}.basic',
 'cookietemple.create.templates.web.website_python.flask.{{ '
 'cookiecutter.project_slug_no_hyphen }}.{{ '
 'cookiecutter.project_slug_no_hyphen }}.errors',
 'cookietemple.create.templates.web.website_python.flask.{{ '
 'cookiecutter.project_slug_no_hyphen }}.{{ '
 'cookiecutter.project_slug_no_hyphen }}.main',
 'cookietemple.create.templates.web.website_python.flask.{{ '
 'cookiecutter.project_slug_no_hyphen }}.{{ '
 'cookiecutter.project_slug_no_hyphen }}.models',
 'cookietemple.create.templates.web.website_python.flask.{{ '
 'cookiecutter.project_slug_no_hyphen }}.{{ '
 'cookiecutter.project_slug_no_hyphen }}.services',
 'cookietemple.custom_cli',
 'cookietemple.info',
 'cookietemple.lint',
 'cookietemple.lint.domains',
 'cookietemple.list',
 'cookietemple.sync',
 'cookietemple.upgrade',
 'cookietemple.util',
 'cookietemple.warp']

package_data = \
{'': ['*'],
 'cookietemple.create.templates': ['cli/cli_java/*',
                                   'cli/cli_java/{{ cookiecutter.project_slug '
                                   '}}/*',
                                   'cli/cli_java/{{ cookiecutter.project_slug '
                                   '}}/.github/*',
                                   'cli/cli_java/{{ cookiecutter.project_slug '
                                   '}}/.github/workflows/*',
                                   'cli/cli_java/{{ cookiecutter.project_slug '
                                   '}}/.settings/*',
                                   'cli/cli_java/{{ cookiecutter.project_slug '
                                   '}}/docs/*',
                                   'cli/cli_java/{{ cookiecutter.project_slug '
                                   '}}/gradle/wrapper/*',
                                   'cli/cli_java/{{ cookiecutter.project_slug '
                                   '}}/makefiles/*',
                                   'cli/cli_java/{{ cookiecutter.project_slug '
                                   '}}/src/main/java/{{ '
                                   'cookiecutter.group_domain }}/{{ '
                                   'cookiecutter.group_organization }}/*',
                                   'cli/cli_java/{{ cookiecutter.project_slug '
                                   '}}/src/test/java/{{ '
                                   'cookiecutter.group_domain }}/{{ '
                                   'cookiecutter.group_organization }}/*',
                                   'cli/cli_python/*',
                                   'common_files/*',
                                   'common_files/{{cookiecutter.commonName}}/*',
                                   'common_files/{{cookiecutter.commonName}}/.github/*',
                                   'common_files/{{cookiecutter.commonName}}/.github/ISSUE_TEMPLATE/*',
                                   'common_files/{{cookiecutter.commonName}}/.github/workflows/*',
                                   'gui/gui_java/*',
                                   'gui/gui_java/{{ cookiecutter.project_slug '
                                   '}}/*',
                                   'gui/gui_java/{{ cookiecutter.project_slug '
                                   '}}/.github/*',
                                   'gui/gui_java/{{ cookiecutter.project_slug '
                                   '}}/.github/workflows/*',
                                   'gui/gui_java/{{ cookiecutter.project_slug '
                                   '}}/docs/*',
                                   'gui/gui_java/{{ cookiecutter.project_slug '
                                   '}}/makefiles/*',
                                   'gui/gui_java/{{ cookiecutter.project_slug '
                                   '}}/src/main/java/*',
                                   'gui/gui_java/{{ cookiecutter.project_slug '
                                   '}}/src/main/java/org/{{ '
                                   'cookiecutter.organization }}/*',
                                   'gui/gui_java/{{ cookiecutter.project_slug '
                                   '}}/src/main/resources/org/{{ '
                                   'cookiecutter.organization }}/*',
                                   'gui/gui_java/{{ cookiecutter.project_slug '
                                   '}}/src/test/java/org/{{ '
                                   'cookiecutter.organization }}/*',
                                   'lib/lib_cpp/*',
                                   'lib/lib_cpp/{{ cookiecutter.project_slug '
                                   '}}/*',
                                   'lib/lib_cpp/{{ cookiecutter.project_slug '
                                   '}}/.github/workflows/*',
                                   'lib/lib_cpp/{{ cookiecutter.project_slug '
                                   '}}/cmake/*',
                                   'lib/lib_cpp/{{ cookiecutter.project_slug '
                                   '}}/docs/*',
                                   'lib/lib_cpp/{{ cookiecutter.project_slug '
                                   '}}/include/{{ cookiecutter.project_slug '
                                   '}}/*',
                                   'lib/lib_cpp/{{ cookiecutter.project_slug '
                                   '}}/makefiles/*',
                                   'lib/lib_cpp/{{ cookiecutter.project_slug '
                                   '}}/src/*',
                                   'lib/lib_cpp/{{ cookiecutter.project_slug '
                                   '}}/test/*',
                                   'lib/lib_cpp/{{ cookiecutter.project_slug '
                                   '}}/test/src/*',
                                   'pub/thesis_latex/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/.github/workflows/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Abstract/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Acknowledgement/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Appendix1/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Chapter1/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Chapter2/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Chapter2/Figs/Raster/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Chapter2/Figs/Vector/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Chapter3/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Declaration/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Dedication/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Figs/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Figs/CollegeShields/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Figs/CollegeShields/src/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/Preamble/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/References/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/hooks/*',
                                   'pub/thesis_latex/{{cookiecutter.project_slug}}/sty/*',
                                   'web/website_python/flask/*'],
 'cookietemple.create.templates.cli.cli_python.{{ cookiecutter.project_slug_no_hyphen }}': ['.github/*',
                                                                                            '.github/workflows/*',
                                                                                            'docs/*',
                                                                                            'makefiles/*'],
 'cookietemple.create.templates.common_files.{{cookiecutter.commonName}}.docs': ['_static/*'],
 'cookietemple.create.templates.web.website_python.flask.{{ cookiecutter.project_slug_no_hyphen }}': ['.github/*',
                                                                                                      '.github/workflows/*',
                                                                                                      'deployment_scripts/*',
                                                                                                      'docs/*',
                                                                                                      'frontend_templates/solidstate/*',
                                                                                                      'frontend_templates/solidstate/assets/css/*',
                                                                                                      'frontend_templates/solidstate/assets/images/*',
                                                                                                      'frontend_templates/solidstate/assets/js/*',
                                                                                                      'frontend_templates/solidstate/assets/sass/*',
                                                                                                      'frontend_templates/solidstate/assets/sass/base/*',
                                                                                                      'frontend_templates/solidstate/assets/sass/components/*',
                                                                                                      'frontend_templates/solidstate/assets/sass/layout/*',
                                                                                                      'frontend_templates/solidstate/assets/sass/libs/*',
                                                                                                      'frontend_templates/solidstate/assets/webfonts/*',
                                                                                                      'makefiles/*'],
 'cookietemple.create.templates.web.website_python.flask.{{ cookiecutter.project_slug_no_hyphen }}.{{ cookiecutter.project_slug_no_hyphen }}': ['static/*',
                                                                                                                                                'static/assets/css/*',
                                                                                                                                                'static/assets/images/*',
                                                                                                                                                'static/assets/js/*',
                                                                                                                                                'static/assets/sass/base/*',
                                                                                                                                                'static/assets/sass/components/*',
                                                                                                                                                'static/assets/sass/layout/*',
                                                                                                                                                'static/assets/sass/libs/*',
                                                                                                                                                'static/assets/webfonts/*',
                                                                                                                                                'templates/*',
                                                                                                                                                'templates/auth/*',
                                                                                                                                                'templates/errors/*',
                                                                                                                                                'translations/de/LC_MESSAGES/*'],
 'cookietemple.warp': ['warp_executables/*']}

install_requires = \
['GitPython>=3.1.17,<4.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'cffi>=1.14.5,<2.0.0',
 'click>=8.0.1,<9.0.0',
 'cookiecutter>=1.7.2,<2.0.0',
 'cryptography>=3.4.7,<4.0.0',
 'packaging>=20.9,<22.0',
 'pygithub>=1.54.1,<2.0.0',
 'pynacl>=1.4.0,<2.0.0',
 'questionary>=1.9.0,<2.0.0',
 'requests>=2.25.1,<3.0.0',
 'rich>=10.2.2,<11.0.0',
 'ruamel.yaml>=0.17.4,<0.18.0']

entry_points = \
{'console_scripts': ['cookietemple = cookietemple.__main__:main']}

setup_kwargs = {
    'name': 'cookietemple',
    'version': '1.3.10',
    'description': 'A cookiecutter based project template creation tool supporting several domains and languages with advanced linting, syncing and standardized workflows to get your project kickstarted in no time.',
    'long_description': "|pic1|\n\n.. |pic1| image:: https://user-images.githubusercontent.com/21954664/83797925-a7019400-a6a3-11ea-86ad-44ad00e24234.png\n   :width: 75%\n\n-----------------------------------------------------------\n\n|\n\n.. image:: https://github.com/zethson/cookietemple/workflows/Build%20Cookietemple%20Package/badge.svg\n        :target: https://github.com/zethson/cookietemple/workflows/Build%20Cookietemple%20Package/badge.svg\n        :alt: Github Workflow Build cookietemple Status\n\n.. image:: https://github.com/cookiejar/cookietemple/actions/workflows/run_tests.yml/badge.svg\n        :target: https://github.com/cookiejar/cookietemple/actions/workflows/run_tests.yml/badge.svg\n        :alt: Github Workflow Tests Status\n\n.. image:: https://img.shields.io/pypi/v/cookietemple.svg\n        :target: https://pypi.python.org/pypi/cookietemple\n        :alt: PyPi Status\n\n.. image:: https://img.shields.io/github/license/cookiejar/cookietemple\n        :target: https://github.com/cookiejar/cookietemple/blob/master/LICENSE\n        :alt: Apache 2.0 license\n\n.. image:: https://readthedocs.org/projects/cookietemple/badge/?version=latest\n        :target: https://cookietemple.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n\n.. image:: https://codecov.io/gh/cookiejar/cookietemple/branch/master/graph/badge.svg?token=dijn0M0p7m\n        :target: https://codecov.io/gh/cookiejar/cookietemple\n        :alt: Codecov Status\n\n.. image:: https://flat.badgen.net/dependabot/thepracticaldev/dev.to?icon=dependabot\n        :target: https://flat.badgen.net/dependabot/thepracticaldev/dev.to?icon=dependabot\n        :alt: Dependabot Enabled\n\n.. image:: https://zenodo.org/badge/202421008.svg\n        :target: https://zenodo.org/badge/latestdoi/202421008\n        :alt: Zenodo ID\n\n.. image:: https://img.shields.io/discord/708008788505919599?color=passing&label=Discord%20Chat&style=flat-square\n        :target: https://discord.gg/PYF8NUk\n        :alt: Discord\n\n.. image:: https://img.shields.io/twitter/follow/cookiejarorg?color=green&style=flat-square\n        :target: https://twitter.com/cookiejarorg\n        :alt: Twitter Follow\n\nA cookiecutter based project template creation tool supporting several domains and languages with advanced linting, syncing and standardized workflows to get your project kickstarted in no time.\n\n* Documentation: https://cookietemple.readthedocs.io .\n\ncookietemple overview\n========================\n\nInstalling\n---------------\n\nStart your journey with cookietemple by installing it via ``$ pip install cookietemple``.\n\nSee `Installation  <https://cookietemple.readthedocs.io/en/latest/readme.html#installing>`_.\n\nconfig\n------\nConfigure cookietemple to get started.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/97928842-1faa7080-1d68-11eb-8c82-39d73d662466.gif\n\nSee `Configuring cookietemple <https://cookietemple.readthedocs.io/en/latest/config.html>`_\n\nlist\n----\nList all available cookietemple templates.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/97928681-d9eda800-1d67-11eb-880d-9d4f8037872b.gif\n\nSee `Listing all templates <https://cookietemple.readthedocs.io/en/latest/list_info.html#list>`_.\n\ninfo\n----\nGet detailed information on a cookietemple template.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/97928788-03a6cf00-1d68-11eb-8c35-851c792ecf02.gif\n\nSee `Get detailed template information <https://cookietemple.readthedocs.io/en/latest/list_info.html#info>`_.\n\ncreate\n------\nKickstart your customized project with one of cookietemple's templates in no time.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/97928626-bb87ac80-1d67-11eb-938f-db2db223d792.gif\n\nSee `Create a project <https://cookietemple.readthedocs.io/en/latest/create.html>`_.\n\nlint\n----\nUse advanced linting to ensure your project always adheres to cookietemple's standards.\n\n.. image:: https://user-images.githubusercontent.com/31141763/97929216-f3432400-1d68-11eb-88b8-391fdfd2f4c9.gif\n\nSee `Linting your project <https://cookietemple.readthedocs.io/en/latest/lint.html>`_\n\nbump-version\n------------\nBump your project version with many configurable options.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/97928562-998e2a00-1d67-11eb-9651-5d7c906e2e88.gif\n\nSee `Bumping the version of an existing project  <https://cookietemple.readthedocs.io/en/latest/bump_version.html>`_.\n\nsync\n------\nSync your project with the latest cookietemple release to get the latest template features.\n\n.. figure:: https://user-images.githubusercontent.com/31141763/97928912-3c46a880-1d68-11eb-8372-8f96370a1b02.gif\n\nSee `Syncing a project <https://cookietemple.readthedocs.io/en/latest/sync.html>`_.\n\nwarp\n----\nCreate a self contained executable.\nCurrently, cookietemple does not ship any templates anymore, where this may be required.\n\nSee `Warping a project <https://cookietemple.readthedocs.io/en/latest/warp.html>`_.\n\nupgrade\n-------\nCheck whether you are using the latest cookietemple version and update automatically to benefit from the latest features.\n\nSee `<https://cookietemple.readthedocs.io/en/latest/upgrade.html>`_.\n\n\nProjects using cookietemple\n---------------------------\n\n* `cookietemple website <https://github.com/cookiejar/cookietemple_website>`_\n* `system-intelligence <https://github.com/mlf-core/system-intelligence>`_\n* `mlf-core <https://github.com/mlf-core/mlf-core>`_\n\nContributing\n------------\n\ncookietemple is a huge open-source effort and highly welcomes all contributions! Join our `Discord Channel <https://discord.gg/PYF8NUk>`_.\nPlease read `contributing  <https://cookietemple.readthedocs.io/en/latest/contributing.html>`_ to find out how you can contribute.\n\nAuthors\n-------\n\ncookietemple was initiated and developed by `Lukas Heumos (Github)  <https://github.com/zethson>`_ and `Philipp Ehmele (Github) <https://github.com/Imipenem>`_.\nA full list of contributors is available on our `statistics webpage <https://www.cookietemple.com/stats>`_.\n",
    'author': 'Philipp Ehmele',
    'author_email': 'philipp_ehm@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://cookietemple.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<3.10',
}


setup(**setup_kwargs)
