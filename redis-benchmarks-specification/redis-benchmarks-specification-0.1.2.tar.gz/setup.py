# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['redis_benchmarks_specification',
 'redis_benchmarks_specification.__api__',
 'redis_benchmarks_specification.__builder__',
 'redis_benchmarks_specification.__common__',
 'redis_benchmarks_specification.__self_contained_coordinator__',
 'redis_benchmarks_specification.__setups__']

package_data = \
{'': ['*'],
 'redis_benchmarks_specification': ['setups/builders/*',
                                    'setups/platforms/*',
                                    'setups/topologies/*',
                                    'test-suites/*']}

install_requires = \
['Flask-HTTPAuth>=4.4.0,<5.0.0',
 'Flask>=2.0.1,<3.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'Werkzeug>=2.0.1,<3.0.0',
 'argparse>=1.4.0,<2.0.0',
 'docker>=4.4.4,<5.0.0',
 'flask-restx>=0.5.0,<0.6.0',
 'marshmallow>=3.12.2,<4.0.0',
 'psutil>=5.8.0,<6.0.0',
 'redis>=3.5.3,<4.0.0',
 'redisbench-admin>=0.4.8,<0.5.0',
 'tox-docker>=3.0.0,<4.0.0']

entry_points = \
{'console_scripts': ['redis-benchmarks-spec-api = '
                     'redis_benchmarks_specification.__api__.api:main',
                     'redis-benchmarks-spec-builder = '
                     'redis_benchmarks_specification.__builder__.builder:main',
                     'redis-benchmarks-spec-sc-coordinator = '
                     'redis_benchmarks_specification.__self_contained_coordinator__.self_contained_coordinator:main']}

setup_kwargs = {
    'name': 'redis-benchmarks-specification',
    'version': '0.1.2',
    'description': 'The Redis benchmarks specification describes the cross-language/tools requirements and expectations to foster performance and observability standards around redis related technologies. Members from both industry and academia, including organizations and individuals are encouraged to contribute.',
    'long_description': None,
    'author': 'filipecosta90',
    'author_email': 'filipecosta.90@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
