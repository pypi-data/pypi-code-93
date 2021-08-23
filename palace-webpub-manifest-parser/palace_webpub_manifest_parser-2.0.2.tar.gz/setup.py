# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['webpub_manifest_parser',
 'webpub_manifest_parser.core',
 'webpub_manifest_parser.epub',
 'webpub_manifest_parser.odl',
 'webpub_manifest_parser.opds2',
 'webpub_manifest_parser.rwpm']

package_data = \
{'': ['*']}

install_requires = \
['enum34>=1.1.10,<2.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'multipledispatch>=0.6.0,<0.7.0',
 'pyrsistent==0.16.1',
 'python-dateutil>=2.8.2,<3.0.0',
 'rfc3987>=1.3.8,<2.0.0',
 'uritemplate>=3.0.1,<4.0.0']

setup_kwargs = {
    'name': 'palace-webpub-manifest-parser',
    'version': '2.0.2',
    'description': 'A parser for the Readium Web Publication Manifest, OPDS 2.0 and ODL formats.',
    'long_description': '# webpub manifest parser\n\n[![Lint & Run Tests](https://github.com/ThePalaceProject/webpub-manifest-parser/actions/workflows/lint-test.yml/badge.svg)](https://github.com/ThePalaceProject/webpub-manifest-parser/actions/workflows/lint-test.yml)\n[![PyPI](https://img.shields.io/pypi/v/palace-webpub-manifest-parser)](https://pypi.org/project/palace-webpub-manifest-parser/)\n\nA parser for the [Readium Web Publication Manifest (RWPM)](https://github.com/readium/webpub-manifest), [Open Publication Distribution System 2.0 (OPDS 2.0)](https://drafts.opds.io/opds-2.0), and [Open Distribution to Libraries 1.0 (ODL)](https://drafts.opds.io/odl-1.0.html) formats.\n\n## Usage\nInstall the library with `pip`\n```bash\npip install palace-webpub-manifest-parser\n``` \n\n### Pyenv\n\nYou can optionally install the python version to run the library with using pyenv.\n\n1. Install [pyenv](https://github.com/pyenv/pyenv#installation)\n\n3. Install one of the supported Python versions:\n```bash\npyenv install <python-version>\n```\n\n4. Install [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv#installation) plugin\n\n5. Create a virtual environment:\n```bash\npyenv virtualenv <virtual-env-name>\npyenv activate <virtual-env-name>\n```\n\n6. Install the library\n```bash\npip install palace-webpub-manifest-parser\n``` \n\n\n# Setting up a development environment\n\n## Running tests using tox\n1. Make sure that a virtual environment is not activated and deactivate it if needed:\n```bash\ndeactivate\n```\n\n2. Install `tox` and `tox-pyenv` globally:\n```bash\npip install tox tox-pyenv\n```\n\n3. Make your code prettier using isort and black:\n```bash\nmake reformat\n``` \n\n4. Run the linters:\n```bash\nmake lint\n```\n\n5. To run the unit tests use the following command:\n```bash\nmake test-<python-version>\n```\nwhere `<python-version>` is one of supported python versions:\n- py27\n- py36\n- py37\n- py38\n\nFor example, to run the unit test using Python 2.7 run the following command:\n```bash\nmake test-py27\n```\n\n# Releasing\n\nReleases will be automatically published to PyPI when new releases are created on github. We use \n`bump2version` to update the version number, then create a release in github.\n\nTo publish a new release:\n- Bump the version and push it as a branch\n  ```\n  git checkout -b release/vX.X.X\n  pip install bump2version\n  bump2version {part}\n  git push origin release/vX.X.X\n  ```\n- Create a PR for new version\n- Merge PR into `main`\n- Create a release for the version in github\n',
    'author': 'Viacheslav Bessonov',
    'author_email': 'viacheslav.bessonov@hilbertteam.com',
    'maintainer': 'Viacheslav Bessonov',
    'maintainer_email': 'viacheslav.bessonov@hilbertteam.com',
    'url': 'https://github.com/ThePalaceProject/python-webpub-manifest-parser',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
}


setup(**setup_kwargs)
