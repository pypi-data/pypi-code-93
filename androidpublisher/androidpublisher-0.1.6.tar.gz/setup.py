# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['androidpublisher']

package_data = \
{'': ['*']}

install_requires = \
['google-api-python-client>=1.12.8,<2.0.0',
 'oauth2client>=4.1.3,<5.0.0',
 'six>=1.13.0,<2.0.0',
 'typer[all]>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['androidpublisher = androidpublisher.main:app']}

setup_kwargs = {
    'name': 'androidpublisher',
    'version': '0.1.6',
    'description': '',
    'long_description': '# Android Publisher\n\n**Usage**:\n\n```console\n$ androidpublisher [OPTIONS] COMMAND [ARGS]...\n```\n\n**Options**:\n\n* `--install-completion`: Install completion for the current shell.\n* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.\n* `--help`: Show this message and exit.\n\n**Commands**:\n\n* `upload`\n\n## `androidpublisher upload`\n\n**Usage**:\n\n```console\n$ androidpublisher upload [OPTIONS] PACKAGE_NAME\n```\n\n**Arguments**:\n\n* `PACKAGE_NAME`: [required]\n\n**Options**:\n\n* `--aab-file FILE`: [default: app.aab]\n* `--track [internal|alpha|beta|production|rollout]`: [default: internal]\n* `--json-key FILE`: [default: credential.json]\n* `--help`: Show this message and exit.\n',
    'author': 'leynier',
    'author_email': 'leynier41@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
