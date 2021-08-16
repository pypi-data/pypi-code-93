# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyparam']

package_data = \
{'': ['*']}

install_requires = \
['diot', 'python-simpleconf', 'rich']

setup_kwargs = {
    'name': 'pyparam',
    'version': '0.4.9',
    'description': 'Powerful parameter processing.',
    'long_description': '# pyparam\n[![pypi][1]][2] [![pypi][10]][11] [![codacy quality][4]][6] [![codacy quality][7]][6] [![docs][12]][5] ![github action][3] ![pyver][8]\n\nPowerful parameter processing\n\n## Features\n- Command line argument parser (with subcommand support)\n- Rich type support, including `py`, `json`, `namespace`, etc.\n- Type overwriting for parameters from command line\n- Arbitrary parsing arguments from command line\n- Automatic help page assembling\n- Help page customization\n- Callbacks for option values\n- Parameter loading from configuration files\n\n## Installation\n```shell\npip install -U pyparam\n```\n\n## Documentation\n[https://pwwang.github.io/pyparam/][5]\n\n## Basic usage\n\n`example.py`\n\n```python\nfrom rich import print\nfrom pyparam import Params\n# program name, otherwise sys.argv[0]\nparams = Params(prog=\'pyparam\', desc="An example for {prog}")\n# adding parameters\nparams.add_param(\'i, int\', type=int,\n                 desc="An integer argument.")\nparams.add_param(\'float\', default=0.1, # type float implied\n                 desc="A float argument.")\nparams.add_param(\'str\', type=str,\n                 desc="A str argument.")\nparams.add_param(\'flag\', type=bool,\n                 desc="A flag argument.")\nparams.add_param(\'c,count\', type=\'count\',\n                 desc="A count argument.")\nparams.add_param(\'a\', type=\'auto\', type_frozen=False,\n                 desc="Value will be automatically casted.")\nparams.add_param(\'py\', type=\'py\',\n                 desc="Value will be evaluated by `ast.literal_eval`.")\nparams.add_param(\'json\', type=\'json\',\n                 desc="Value will be converted using `json.loads`.")\nparams.add_param(\'list\', type=\'list\',\n                 desc="Values will be accumulated.")\nparams.add_param(\'path\', type=\'path\', required=True,\n                 desc="Value will be casted into `pathlib.Path`.",\n                 callback=( # check if path exists\n                     lambda path: ValueError(\'File does not exist.\')\n                     if not path.exists() else path\n                 ))\nparams.add_param(\'choice\', type=\'choice\', default=\'medium\',\n                 choices=[\'small\', \'medium\', \'large\'],\n                 desc="One of {choices}.")\nparams.add_param(\'config.ncores\', default=1, # namespace config implied\n                 argname_shorten=False,\n                 desc=\'Number of cores to use.\')\n\nprint(vars(params.parse()))\n```\n\nTry it out:\n```sh\n$ python example.py\n```\n\n![help](./pyparam-help.png)\n\n```sh\n$ python example.py \\\n    -i2 \\\n    --float 0.5 \\\n    --str abc \\\n    -ccc \\\n    -a:int 1 \\\n    --py "{1,2,3}" \\\n    --json "{\\"a\\": 1}" \\\n    --list 1 2 3 \\\n    --choice large \\\n    --path . \\\n    --config.ncores 4\n```\n```python\n{\n    \'i\': 2,\n    \'int\': 2,\n    \'float\': 0.5,\n    \'str\': \'abc\',\n    \'flag\': False,\n    \'c\': 3,\n    \'count\': 3,\n    \'a\': 1,\n    \'py\': {1, 2, 3},\n    \'json\': {\'a\': 1},\n    \'list\': [1, 2, 3],\n    \'path\': PosixPath(\'.\'),\n    \'choice\': \'large\',\n    \'config\': Namespace(ncores=4)\n}\n```\n\nTry more features with:\n```sh\n$ python -m pyparam\n```\n\n## Shell completions\n\nHere is how the command completion in `fish` works:\n\n![pyparam-completions](./pyparam-completions.gif)\n\nCheck the [documentation][13], as well as the `__main__.py` to see how the completion works.\n\n\n[1]: https://img.shields.io/pypi/v/pyparam.svg?style=flat-square\n[2]: https://pypi.org/project/pyparam/\n[3]: https://img.shields.io/github/workflow/status/pwwang/pyparam/Build%20and%20Deploy?style=flat-square\n[4]: https://img.shields.io/codacy/grade/370aa0074595445188b01dc8dba47fe5.svg?style=flat-square\n[5]: https://pwwang.github.io/pyparam/\n[6]: https://app.codacy.com/project/pwwang/pyparam/dashboard\n[7]: https://img.shields.io/codacy/coverage/370aa0074595445188b01dc8dba47fe5.svg?style=flat-square\n[8]: https://img.shields.io/pypi/pyversions/pyparam.svg?style=flat-square\n[9]: https://raw.githubusercontent.com/pwwang/pyparam/master/docs/static/help.png\n[10]: https://img.shields.io/github/tag/pwwang/pyparam.svg?style=flat-square\n[11]: https://github.com/pwwang/pyparam\n[12]: https://img.shields.io/github/workflow/status/pwwang/pyparam/Build%20Docs?label=docs&style=flat-square\n[13]: https://pwwang.github.io/pyparam/shellCompletion/\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pwwang/pyparam',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
