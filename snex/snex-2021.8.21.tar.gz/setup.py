# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['snex', 'snex.cli']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'pyhocon>=0.3.57,<0.4.0',
 'pystache>=0.5.4,<0.6.0',
 'pyyaml>=5.4.1,<6.0.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['snex = snex.cli:main']}

setup_kwargs = {
    'name': 'snex',
    'version': '2021.8.21',
    'description': 'snex - snippet extractor',
    'long_description': '# snex - snippet extractor\n\n[(Accompanying blog post)](https://bargsten.org/wissen/snex/)\n\nExtract snippets for blog posts or examples.\n\nHow to use\n\n## Installation\n\n    pip install snex\n\n## Tag Snippets\n\nLet\'s assume that you have a project in `/path/to/your/project`. You navigate to the\nregion where you want to extract a snippet and tag it as follows (`# ` is regarded as\ncomment prefix):\n\n    # :snippet snippet-name-without-whitespace\n\n    def foobar():\n       doit()\n    foobar()\n\n    # :endsnippet\n\n- Empty lines after the start and before the end are removed.\n- _A snippet name is mandatory._\n- The snippet `name` is sanitized to prevent malicious code to overwrite arbitrary files\n  on your system.\n\n### Advanced snippet tagging\n\nYou can also overwrite the `lang` config to use a different language for this snippet.\n\n```\n# :snippet snippet-name-without-whitespace lang: scala\n```\n\nEverything after the snippet name is parsed as YAML dict:\n`{ $text_after_snippet_name }`, e.g. `lang: scala, other_param: "hello world"` is parsed\nas `{ lang: scala, other_param: "hello world" }` YAML.\n\nThis means that you can also customise your parameter substitutions with a config like:\n\n````\nconfig {\n  default {\n    "output_template": "```{{lang}} - {{other_param}}\\n{{{snippet}}}\\n```\\n",\n    "valid_param_keys": [ "lang", "name", "other_param" ]\n    ...\n  }\n}\n````\n\nThe output template is parsed as [mustache template](https://mustache.github.io/).\n\n## Setup\n\ncreate a snex.conf in the root directory of a project you want to create snippets from:\n\n    config {\n      default {\n        output_path: "snippets"\n        comment_prefix: "# "\n        comment_suffix: ""\n      }\n\n      src {\n        lang: "python"\n        root: "src"\n        glob: "**/*.py"\n      }\n      github {\n        comment_prefix: "# "\n        lang: "python"\n        path: "https://raw.githubusercontent.com/jwbargsten/snex/master/src/snex/core.py"\n      }\n    }\n\nThe config syntax is\n[HOCON](https://github.com/typesafehub/config/blob/master/HOCON.md), under the hood\n[pyhocon](https://github.com/chimpler/pyhocon).\n\nYou have 3 layers of settings in a section:\n\n1.  [the global default config](docs/snippets/src-global-default-config.md) in\n    `docs/snippets/global-default-config.md`\n2.  the config section `default` in your `snex.conf` file (which overwrites the global\n    default).\n3.  the specific config section in your `snex.conf` (the section name is prefix for\n    snippets `default` is reserved.). The configuration in a specific section overwrites\n    the default section which overwrites the global default config.\n\n## Run\n\nYou created a `/path/to/your/project/snex.conf` like described in the previous topic.\n\n### From the project directory\n\n    cd /path/to/your/project\n    snex\n\nThis will read `snex.conf` in the current directory and dump the snippets into the\nconfigured `output_path`.\n\n### From a different directory\n\n    snex /path/to/your/project\n\nThis will read `/path/to/your/project/snex.conf` and dump the snippets into the\nconfigured `output_path`.\n\n### From a different directory to a different snippet output directory\n\n    snex /path/to/your/project /path/custom/snippet/output/dir\n\nThis will read `/path/to/your/project/snex.conf` and dump the snippets into\n`/path/custom/snippet/output/dir`.\n\n**TAKE CARE**\n\nThis invocation will overwrite the output dir of all defined config sections. Which\nmeans that all snippets are dumped into the same directory.\n\n## Caveats (or features)\n\n- Snippets are overwritten without confirmation. This makes it easy to update\n  everything, but you have to take care that you will not overwrite stuff you want to\n  keep.\n',
    'author': 'Joachim Bargsten',
    'author_email': 'jw@bargsten.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jwbargsten/snex',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
