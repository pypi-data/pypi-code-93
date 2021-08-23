# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dataconf']

package_data = \
{'': ['*']}

install_requires = \
['pyhocon>=0.3.54,<0.4.0', 'python-dateutil>=2.8.1,<3.0.0']

entry_points = \
{'console_scripts': ['dataconf = dataconf.cli:run']}

setup_kwargs = {
    'name': 'dataconf',
    'version': '0.1.5',
    'description': 'Lightweight configuration with automatic dataclasses parsing (HOCON/JSON/YAML/PROPERTIES)',
    'long_description': '# Dataconf\n\n[![Actions Status](https://github.com/zifeo/dataconf/workflows/CI/badge.svg)](https://github.com/zifeo/dataconf/actions)\n[![PyPI version](https://badge.fury.io/py/dataconf.svg)](https://badge.fury.io/py/dataconf)\n\nLightweight configuration with automatic dataclasses parsing (hocon/json/yaml/properties files).\n\n## Getting started\n\nRequires at least Python 3.8.\n\n```bash\n# pypi\npip install dataconf\npoetry add dataconf\n\n# master\npip install --upgrade git+https://github.com/zifeo/dataconf.git\npoetry add git+https://github.com/zifeo/dataconf.git\n\n# dev\npoetry install\npre-commit install\n```\n\n## Usage\n\n```python\nfrom dataclasses import dataclass, field\nfrom typing import List, Dict, Text, Union\nfrom dateutil.relativedelta import relativedelta\nimport dataconf\n\nconf = """\nstr_name = test\nstr_name = ${HOSTNAME}\nfloat_num = 2.2\nlist_data = [\n    a\n    b\n]\nnested {\n    a = test\n}\nnested_list = [\n    {\n        a = test1\n    }\n]\nduration = 2s\nunion = 1\n"""\n\n@dataclass\nclass Nested:\n    a: Text\n\n@dataclass\nclass Config:\n    str_name: Text\n    float_num: float\n    list_data: List[Text]\n    nested: Nested\n    nested_list: List[Nested]\n    duration: relativedelta\n    union: Union[Text, int]\n    default: Text = \'hello\'\n    default_factory: Dict[Text, Text] = field(default_factory=dict)\n\nprint(dataconf.load(conf, Config))\n# TestConf(test=\'pc.home\', float=2.1, default=\'hello\', list=[\'a\', \'b\'], nested=Nested(a=\'test\'), nested_list=[Nested(a=\'test1\')], duration=relativedelta(seconds=+2), default_factory={}, union=1)\n```\n\n```python\nimport dataconf\n\nconf = dataconf.loads(\'confs/test.hocon\', Config)\nconf = dataconf.loads(\'confs/test.json\', Config)\nconf = dataconf.loads(\'confs/test.yaml\', Config)\nconf = dataconf.loads(\'confs/test.properties\', Config)\n\ndataconf.dumps(\'confs/test.hocon\', out=\'hocon\')\ndataconf.dumps(\'confs/test.json\', out=\'json\')\ndataconf.dumps(\'confs/test.yaml\', out=\'yaml\')\ndataconf.dumps(\'confs/test.properties\', out=\'properties\')\n```\n\nFollows same api as python JSON package (e.g. `load`, `loads`, `dump`, `dumps`). \nFor full HOCON capabilities see [here](https://github.com/chimpler/pyhocon/#example-of-hocon-file).\n\n## CI\n\n```shell\ndataconf -c confs/test.hocon -m tests.configs -d TestConf -o hocon\n# dataconf.exceptions.TypeConfigException: expected type <class \'datetime.timedelta\'> at .duration, got <class \'int\'>\n```\n',
    'author': None,
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/zifeo/dataconf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
