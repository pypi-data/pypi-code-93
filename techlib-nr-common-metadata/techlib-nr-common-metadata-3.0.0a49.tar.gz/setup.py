# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nr_common_metadata',
 'nr_common_metadata.jsonschemas',
 'nr_common_metadata.jsonschemas.nr_common_metadata',
 'nr_common_metadata.mapping_includes',
 'nr_common_metadata.mapping_includes.v7',
 'nr_common_metadata.mappings',
 'nr_common_metadata.mappings.v7',
 'nr_common_metadata.mappings.v7.nr_common_metadata',
 'nr_common_metadata.marshmallow']

package_data = \
{'': ['*']}

install_requires = \
['IDUtils>=1.1.8,<2.0.0', 'isbnlib>=3.10.8,<4.0.0', 'python-stdnum>=1.16,<2.0']

extras_require = \
{'docs': ['sphinx>=1.5.1,<2.0.0']}

entry_points = \
{'invenio_jsonschemas.schemas': ['nr_common_metadata = '
                                 'nr_common_metadata.jsonschemas'],
 'oarepo_mapping_includes': ['nr_common_metadata = '
                             'nr_common_metadata.mapping_includes']}

setup_kwargs = {
    'name': 'techlib-nr-common-metadata',
    'version': '3.0.0a49',
    'description': 'NR common data types',
    'long_description': '# nr-common-metadata\n\n[![Build Status](https://travis-ci.org/Narodni-repozitar/nr-common.svg?branch=master)](https://travis-ci.org/Narodni-repozitar/nr-common)\n[![Coverage Status](https://coveralls.io/repos/github/Narodni-repozitar/nr-common/badge.svg)](https://coveralls.io/github/Narodni-repozitar/nr-common)\n\nDisclaimer: The library is part of the Czech National Repository, and therefore the README is written in Czech.\nGeneral libraries extending [Invenio](https://github.com/inveniosoftware) are concentrated under the [Oarepo\n namespace](https://github.com/oarepo).\n \n ## Instalace\n \n Nejedná se o samostatně funkční knihovnu, proto potřebuje běžící Invenio a závislosti Oarepo.\n Knihovna se instaluje klasicky přes pip\n \n```bash\npip install techlib-nr-common-metadata\n```\n\nPro testování a/nebo samostané fungování knihovny je nutné instalovat tests z extras.\n\n```bash\npip install -e .[tests]\n```\n\n## Účel\n\nKnihovna obsahuje obecný metadatový model Národního repozitáře (Marshmallow, JSON schema a Elastisearch mapping).\nVšechny tyto části lze \n"podědit" v dalších metadatových modelech.\n\nKnihovna není samostatný model pro "generic" věci - ten je v nr-generic.\n',
    'author': 'Daniel Kopecký',
    'author_email': 'Daniel.Kopecky@techlib.cz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
