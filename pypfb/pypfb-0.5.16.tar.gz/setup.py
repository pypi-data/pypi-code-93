# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['pfb', 'pfb.commands', 'pfb.etl', 'pfb.exporters', 'pfb.importers']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.3.1,<6.0.0',
 'aiohttp>=3.6.3,<4.0.0',
 'click>=7.1.2,<8.0.0',
 'dictionaryutils>=3.2.0,<4.0.0',
 'fastavro<=1.4.1',
 'gdcdictionary>=1.2.0,<2.0.0',
 'gen3>=4.2.0,<5.0.0',
 'python-json-logger>=0.1.11,<0.2.0']

extras_require = \
{':python_version <= "3.8"': ['importlib_metadata>=1.3.0,<2.0.0']}

entry_points = \
{'console_scripts': ['pfb = pfb.cli:main'],
 'pfb.plugins': ['add = pfb.commands.add',
                 'etl = pfb.commands.etl',
                 'from_gen3dict = pfb.importers.gen3dict',
                 'from_json = pfb.importers.json',
                 'from_tsv = pfb.importers.tsv',
                 'import = pfb.commands.import',
                 'rename = pfb.commands.rename',
                 'show = pfb.commands.show',
                 'to_gremlin = pfb.exporters.gremlin',
                 'to_tsv = pfb.exporters.tsv']}

setup_kwargs = {
    'name': 'pypfb',
    'version': '0.5.16',
    'description': 'Python SDK for PFB format',
    'long_description': None,
    'author': 'CTDS UChicago',
    'author_email': 'cdis@uchicago.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<=3.8',
}


setup(**setup_kwargs)
