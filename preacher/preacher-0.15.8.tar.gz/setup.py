# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['preacher',
 'preacher.app',
 'preacher.app.cli',
 'preacher.compilation',
 'preacher.compilation.extraction',
 'preacher.compilation.request',
 'preacher.compilation.scenario',
 'preacher.compilation.util',
 'preacher.compilation.verification',
 'preacher.compilation.yaml',
 'preacher.compilation.yaml.tag',
 'preacher.core',
 'preacher.core.extraction',
 'preacher.core.extraction.impl',
 'preacher.core.request',
 'preacher.core.scenario',
 'preacher.core.scenario.util',
 'preacher.core.scheduling',
 'preacher.core.unit',
 'preacher.core.util',
 'preacher.core.value',
 'preacher.core.value.impl',
 'preacher.core.verification',
 'preacher.plugin',
 'preacher.presentation',
 'preacher.presentation.listener']

package_data = \
{'': ['*'],
 'preacher': ['resources/report/html/*', 'resources/report/html/macros/*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'click>=8.0.1,<9.0.0',
 'colorama>=0.4.1,<0.5.0',
 'jq>=1.1.2,<2.0.0',
 'lxml>=4.4,<5.0',
 'pluggy>=0.13.1,<0.14.0',
 'pyhamcrest>=2.0,<3.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'requests>=2.21,<3.0',
 'yamlen>=0.1.0,<0.2.0']

entry_points = \
{'console_scripts': ['preacher-cli = preacher.app.cli.main:main'],
 'preacher': ['preacher-plugin-default = preacher.plugin.impl']}

setup_kwargs = {
    'name': 'preacher',
    'version': '0.15.8',
    'description': 'Web API Verification without Coding.',
    'long_description': '# Preacher: Web API Verification without Coding\n\n[![PyPI version](https://badge.fury.io/py/preacher.svg)][PyPI]\n[![Documentation Status](https://readthedocs.org/projects/preacher/badge/?version=latest)][Read the Docs]\n[![CircleCI](https://circleci.com/gh/ymoch/preacher.svg?style=svg)][Circle CI]\n[![Codecov](https://codecov.io/gh/ymoch/preacher/branch/master/graph/badge.svg)][Codecov]\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/ymoch/preacher.svg?logo=lgtm&logoWidth=18)][LGTM]\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)][Black]\n\nPreacher verifies API servers,\nwhich requests to the servers and verify the responses along to given scenarios.\n\nTest scenarios are written only in [YAML][] declaratively, without coding.\nIn spite of that, Preacher can validate your web API flexibly,\nwhich enables you to test using real (neither mocks nor sandboxes) backends.\n\n- Responses are analyzed [jq][] or [XPath][] queries\n- Validation rules are based on [Hamcrest][] (implemented by [PyHamcrest][]).\n\nThe full documentation is available at [preacher.readthedocs.io][Read the Docs].\n\n## Targets\n\n- Flexible validation to test with real backends: neither mocks nor sandboxes.\n  - Matcher-based validation.\n- CI Friendly to automate easily.\n  - A CLI application and YAML-based scenarios.\n\n## Usage\n\nFirst, install Preacher.\n\nThe most basic way to install Preacher is using `pip`. Supports only Python 3.7+.\n\n```sh\n$ pip install preacher\n$ preacher-cli --version\n```\n\nInstead of `pip`, Docker images are also available on\n[Docker Hub](https://hub.docker.com/r/ymoch/preacher)\nas `ymoch/preacher`.\nBy default, the container working directory is `/work`,\nand the host directory may be mounted here.\n\n```sh\n$ docker pull ymock/preacher\n$ docker run -v $PWD:/work ymoch/preacher preacher-cli --version\n```\n\nSecond, write your own scenario.\n\n```yaml\n# scenario.yml\nlabel: An example of a scenario\ncases:\n  - label: An example of a case\n    request: /path/to/foo\n    response:\n      status_code: 200\n      body:\n        - describe: .foo\n          should:\n            equal: bar\n```\n\nThen, run ``preacher-cli`` command.\n\n```sh\n$ preacher-cli -u http://your.domain.com/base scenario.yml\n```\n\nFor more information such as grammer of scenarios,\nsee [the full documentation][Read the Docs].\n\n## License\n\n[![MIT License](https://img.shields.io/badge/License-MIT-brightgreen.svg)][MIT License]\n\nCopyright (c) 2019 Yu MOCHIZUKI\n\n\n[YAML]: https://yaml.org/\n[jq]: https://stedolan.github.io/jq/\n[XPath]: https://www.w3.org/TR/xpath/all/\n[Hamcrest]: http://hamcrest.org/\n[PyHamcrest]: https://pyhamcrest.readthedocs.io/\n[MIT License]: https://opensource.org/licenses/MIT\n\n[Read the Docs]: https://preacher.readthedocs.io/\n[PyPI]: https://badge.fury.io/py/preacher\n[Circle CI]: https://circleci.com/gh/ymoch/preacher\n[Codecov]: https://codecov.io/gh/ymoch/preacher\n[LGTM]: https://lgtm.com/projects/g/ymoch/preacher/context:python\n[Black]: https://github.com/psf/black\n',
    'author': 'Yu Mochizuki',
    'author_email': 'ymoch.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://preacher.readthedocs.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
