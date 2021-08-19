# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mixins']

package_data = \
{'': ['*']}

install_requires = \
['django-filer>=2.0.2,<3.0.0']

extras_require = \
{'cms': ['django-cms>=3.7.3,<4.0.0']}

setup_kwargs = {
    'name': 'giant-mixins',
    'version': '0.3.2',
    'description': 'A mixins app that provides some standard mixins for Giant projects',
    'long_description': '# Giant Mixins\n\nA small, re-usable package which can be used in any project that requires mixins (which is 99% of them)\nThis will include the standard mixins such as TimestampMixin, PublishingMixin and VideoURLMixin\n\n## Installation\n\nTo install the standard app with no extras simply run\n\n    $ poetry add giant-mixins\n\nHowever if your project has django-cms installed then you can make use of the full range of mixins in this app. For this, install the package with the extra dependencies,\n\n    $ poetry add giant-mixins --extras "cms"\n\nYou should then add `"mixins"` to the `INSTALLED_APPS` in your settings file.\n',
    'author': 'Will-Hoey',
    'author_email': 'will.hoey@giantmade.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/giantmade/giant-mixins',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
