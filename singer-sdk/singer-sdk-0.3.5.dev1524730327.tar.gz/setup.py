# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['singer_sdk',
 'singer_sdk.helpers',
 'singer_sdk.samples.sample_tap_countries',
 'singer_sdk.samples.sample_tap_gitlab',
 'singer_sdk.samples.sample_tap_google_analytics',
 'singer_sdk.samples.sample_target_csv',
 'singer_sdk.samples.sample_target_parquet',
 'singer_sdk.streams',
 'singer_sdk.tests',
 'singer_sdk.tests.cookiecutters',
 'singer_sdk.tests.core',
 'singer_sdk.tests.external',
 'singer_sdk.tests.external_snowflake']

package_data = \
{'': ['*'],
 'singer_sdk.samples.sample_tap_countries': ['schemas/*'],
 'singer_sdk.samples.sample_tap_gitlab': ['schemas/*'],
 'singer_sdk.samples.sample_tap_google_analytics': ['resources/*', 'schemas/*'],
 'singer_sdk.tests.core': ['resources/*'],
 'singer_sdk.tests.external': ['.secrets/*'],
 'singer_sdk.tests.external_snowflake': ['.secrets/*']}

install_requires = \
['PyJWT==1.7.1',
 'backoff>=1.8.0,<2.0',
 'click>=7.1.2,<8.0.0',
 'cryptography>=3.4.6,<4.0.0',
 'inflection>=0.5.1,<0.6.0',
 'joblib>=1.0.1,<2.0.0',
 'jsonpath-ng>=1.5.3,<2.0.0',
 'memoization>=0.3.2,<0.4.0',
 'pendulum>=2.1.0,<3.0.0',
 'pipelinewise-singer-python==1.2.0',
 'requests>=2.25.1,<3.0.0',
 'simpleeval>=0.9.10,<0.10.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata'],
 'docs': ['sphinx>=3.5.4,<4.0.0',
          'sphinx-rtd-theme>=0.5.2,<0.6.0',
          'sphinx-copybutton>=0.3.1,<0.4.0',
          'myst-parser>=0.14.0,<0.15.0']}

setup_kwargs = {
    'name': 'singer-sdk',
    'version': '0.3.5.dev1524730327',
    'description': 'A framework for building Singer taps',
    'long_description': None,
    'author': 'Meltano Team and Contributors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<3.9',
}


setup(**setup_kwargs)
