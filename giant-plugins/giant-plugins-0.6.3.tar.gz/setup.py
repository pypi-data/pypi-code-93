# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['giant_plugins',
 'giant_plugins.content_width_image',
 'giant_plugins.content_width_video',
 'giant_plugins.donate',
 'giant_plugins.featured_cta',
 'giant_plugins.hero_image',
 'giant_plugins.logo_grid',
 'giant_plugins.migrations',
 'giant_plugins.page_card',
 'giant_plugins.pullquote',
 'giant_plugins.rich_text',
 'giant_plugins.share_this_page']

package_data = \
{'': ['*'],
 'giant_plugins': ['static/vendor/summernote/*',
                   'static/vendor/summernote/font/*',
                   'static/vendor/summernote/lang/*',
                   'static/vendor/summernote/plugin/databasic/*',
                   'static/vendor/summernote/plugin/hello/*',
                   'static/vendor/summernote/plugin/specialchars/*',
                   'templates/plugins/*',
                   'templates/plugins/logo_grid/*',
                   'templates/plugins/page_card/*',
                   'templates/plugins/pullquote/*']}

install_requires = \
['django-filer', 'giant-mixins>=0.3.2,<0.4.0']

setup_kwargs = {
    'name': 'giant-plugins',
    'version': '0.6.3',
    'description': 'Adds a generic list of plugins for use within projects',
    'long_description': '# Giant Plugins\n\nA re-usable package which can be used in any project that requires a base set of plugins. \n\nThis will include a small set of plugins that are used in a large number of projects, but will not necessarily cover the full requirements. It will also provide a RichText field which can be used in other areas of the project\nThe RichText field uses ![summernote](https://github.com/summernote/summernote/) for styling the WYSIWYG widget.\n\n## Installation\n\nTo install with the package manager, run:\n\n    $ poetry add giant-plugins\n\nYou should then add `"giant_plugins"` to the `INSTALLED_APPS` in `base.py`.  \n\nIn order to run `django-admin` commands you will need to set the `DJANGO_SETTINGS_MODULE` by running\n\n    $ export DJANGO_SETTINGS_MODULE=settings\n\n## Configuration\n\nThis application exposes the following settings:\n\n`SUMMERNOTE_CONFIG` which allows the user to configure a set of options for the redactor. For example the settings below will give you a basic setup,\n\n```\nSUMMERNOTE_CONFIG = (\n    {\n        "iframe": True,\n        "summernote": {\n            "airMode": False,\n            # Change editor size\n            "width": "100%",\n            "height": "480",\n            "lang": None,\n            "toolbar": [\n                ["style", ["style"]],\n                ["font", ["bold", "underline", "clear"]],\n                ["fontname", ["fontname"]],\n                ["color", ["color"]],\n                ["para", ["ul", "ol", "paragraph"]],\n                ["table", ["table"]],\n                ["insert", ["link", "picture", "video"]],\n                ["view", ["fullscreen", "codeview", "help"]],\n            ],\n        },\n    },\n)\n\n```\n\nIn order to specify a form to use for a specific plugin you should add something like this to your settings file:\n\n```\n<PLUGIN_NAME>_FORM = "<path.to.form.FormClass>"\n```\n\nWhere PLUGIN_NAME is the capitalised name of the plugin (e.g `TEXTWITHIMAGEPLUGIN_FORM`) and the path to the form class as a string so it can be imported.\n\n ## Preparing for release\n \n In order to prep the package for a new release on TestPyPi and PyPi there is one key thing that you need to do. You need to update the version number in the `pyproject.toml`.\n This is so that the package can be published without running into version number conflicts. The version numbering must also follow the Semantic Version rules which can be found here https://semver.org/.\n \n \n ## Publishing\n \n Publishing a package with poetry is incredibly easy. Once you have checked that the version number has been updated (not the same as a previous version) then you only need to run two commands.\n \n    $ `poetry build` \n\nwill package the project up for you into a way that can be published.\n \n    $ `poetry publish`\n\nwill publish the package to PyPi. You will need to enter the username and password for the account which can be found in the company password manager',
    'author': 'Will-Hoey',
    'author_email': 'will.hoey@giantmade.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/giantmade/giant-plugins',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
