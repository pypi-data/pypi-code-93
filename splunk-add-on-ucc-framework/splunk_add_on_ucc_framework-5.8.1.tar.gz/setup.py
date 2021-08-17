# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splunk_add_on_ucc_framework',
 'splunk_add_on_ucc_framework.modular_alert_builder',
 'splunk_add_on_ucc_framework.modular_alert_builder.build_core',
 'splunk_add_on_ucc_framework.uccrestbuilder',
 'splunk_add_on_ucc_framework.uccrestbuilder.endpoint']

package_data = \
{'': ['*'],
 'splunk_add_on_ucc_framework': ['arf_dir_templates/*',
                                 'arf_dir_templates/modular_alert_package/${product_id}/appserver/static/*',
                                 'package/appserver/static/js/build/*',
                                 'package/appserver/templates/*',
                                 'package/default/*',
                                 'package/default/data/ui/nav/*',
                                 'package/default/data/ui/views/*',
                                 'schema/*',
                                 'templates/*'],
 'splunk_add_on_ucc_framework.modular_alert_builder.build_core': ['arf_template/*',
                                                                  'arf_template/default_html_theme/*']}

install_requires = \
['defusedxml>=0.7.1,<0.8.0',
 'dunamai==1.5.5',
 'jinja2>=2,<4',
 'jsonschema>=3.2.0,<4.0.0',
 'lxml>=4.3,<5.0',
 'wheel']

entry_points = \
{'console_scripts': ['ucc-gen = splunk_add_on_ucc_framework:main']}

setup_kwargs = {
    'name': 'splunk-add-on-ucc-framework',
    'version': '5.8.1',
    'description': 'Splunk Add-on SDK formerly UCC is a build and code generation framework',
    'long_description': '# SPDX-FileCopyrightText: 2020 Splunk Inc.\n\n# splunk-add-on-ucc-framework\n\n![PyPI](https://img.shields.io/pypi/v/splunk-add-on-ucc-framework)\n![Python](https://img.shields.io/pypi/pyversions/splunk-add-on-ucc-framework.svg)\n\nA framework to generate UI based Splunk Add-ons. It includes UI, Rest handler, Modular input, Oauth, Alert action templates.\n\n> Note: after UCC 5.2 Python 2 specific libraries are not supported anymore.\n> This means if the add-on has `package/lib/py2/requirements.txt` they will \n> not be installed while running `ucc-gen` command. Therefore modular inputs \n> that are supposed to run on Python 2 will not be supported by UCC. \n\n## What is UCC?\n\nUCC stands for  Universal Configuration Console. It is a service for generating Splunk Add-ons which is easily customizable and flexible.\nUCC provides basic UI template for creating Addon\'s UI. It is helpful to control the activity by using hooks and other functionalities.\n\n\n## Features\n\n- Generate UCC based addons for your Splunk Technology Add-ons\n\n## UCC 5\n\nUCC 5 has potentially breaking changes to add-ons using hook extension in the UX. Previously such hooks were limited to un-optimized js files placed in the package.\nAdd-ons may now package such extensions with webpack.\n\n## Requirements\n\n- Addon package and globalConfig.json file\n\n> Note: You may refer the globalConfig.json file [here](https://github.com/splunk/addonfactory-ucc-generator/blob/master/tests/data/globalConfig.json)\n\n\n## Installation\n\n"splunk-add-on-ucc-framework" can be installed via `pip` from `PyPI`:\n\n```bash\n$ pip3 install splunk-add-on-ucc-framework\n```\n\n## pre-commit\n\nPlease visit `pre-commit` quick start [section](https://pre-commit.com/#quick-start).\n\n## How to use\n\nTo build the UCC based addon follow the below steps:\n\n1. Install the `splunk-add-on-ucc-framework` via `pip3`.\n2. Run the `ucc-gen` command.\n3. Make sure that `package` folder and `globalConfig.json` file are present in the addon folder.\n4. The final addon package will be generated, in the `output` folder.\n\n\n## Workflow\n\nBy the running the `ucc-gen` command, the following steps are executed:\n1. Cleaning out the `output` folder.\n2. Retrieve the package ID of addon.\n3. Copy UCC template directory under `output/<package_ID>` directory.\n4. Copy `globalConfig.json` file to `output/<package_ID>/appserver/static/js/build` directory.\n5. Collect and install Addon\'s requirements into `output/<package_ID>/lib` directory of addon\'s package.\n6. For the addon\'s requirements, packages are installed according to following table:\n\n    | File Name            | Description                         | Output directory in UCC build |\n    |----------------------|-------------------------------------|-------------------------------|\n    | lib/requirements.txt     | Python3 compatible packages | output/<package_ID>/lib   |\n\n7. Replace tokens in views.\n8. Copy addon\'s `package/*` to `output/<package_ID>/*` directory.\n9. If an addon requires some additional configurations in packaging than implement the steps in additional_packaging.py\n\n## Params\n\nsplunk-add-on-ucc-framework supports the following params:\n\n| Name       | Description                                                                                              |\n|------------|----------------------------------------------------------------------------------------------------------|\n| source     | Folder containing the app.manifest and app source                                                        |\n| config     | Path to the configuration file, Defaults to GlobalConfig.json in the parent directory of source provided |\n| ta-version | Optional override Current version of TA, Default version is version specified in globalConfig.json a Splunkbase compatible version of SEMVER will be used by default                         |\n',
    'author': 'rfaircloth-splunk',
    'author_email': 'rfaircloth@splunk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/splunk/splunk-add-on-sdk-python/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
