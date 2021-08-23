# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yaml_patch']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.1,<9.0.0', 'ruamel.yaml>=0.17.11,<0.18.0']

entry_points = \
{'console_scripts': ['yaml-patch = yaml_patch.cli:cli']}

setup_kwargs = {
    'name': 'yaml-patch',
    'version': '0.2.1',
    'description': 'Patch yaml strings',
    'long_description': '# yaml-patch\n\nApply patches to a yaml string, keeping most of the formatting and comments.\n\nSome formatting is not kept due to underlying yaml library limitations:\n  - Indentation will be forced to two spaces\n  - Spacing before sequence dashes will be forced to two spaces\n  - Empty lines at the start of the string will be removed\n\n## As a command line tool\n\nYou can pass any number of patches to be applied, they use the following syntax options:\n\n### Patch a single value:\n`<field>.<subfield>=<value>`\n\nExample:\n```bash\nyaml-patch -f test.yml  "spec.replicas=2"\n```\n\n### Patch a value inside a single list item:\n`<field>.[<position]>.<subfield>=<value>`\n\nExample:\n```bash\nyaml-patch -f test.yml  "spec.template.containers.[0].image=\'mycontainer:latest\'"\n```\n\n### Patch a value inside all list items:\n`<field>.[].<subfield>=<value>`\n\nExample:\n```bash\nyaml-patch -f test.yml "spec.template.containers.[].image=\'mycontainer:latest\'"\n```\n\n## As a Python library\n\nTo use `yaml-patch` as a library just import the function and pass patches as dictionary entries.\n\nExample:\n\n```python\nfrom yaml_patch import patch\nfrom textwrap import dedent\n\ndef override_list_all_values():\n    source_yaml = dedent(\n        """\\\n        some_list:\n          - alice\n          - bob\n        """\n    )\n    patches = {"some_list.[]": "charlie"}\n    expected_yaml = dedent(\n        """\\\n        some_list:\n          - charlie\n          - charlie\n        """\n    )\n    assert patch(source_yaml, patches) == expected_yaml\n```',
    'author': 'Diogo de Campos',
    'author_email': 'campos.ddc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/campos-ddc/yaml-patch',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
