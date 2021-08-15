# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nepseutils']

package_data = \
{'': ['*']}

install_requires = \
['cryptography>=3.4.7,<4.0.0',
 'requests>=2.25.1,<3.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'tenacity>=7.0.0,<8.0.0']

setup_kwargs = {
    'name': 'nepseutils',
    'version': '0.2.0',
    'description': 'Collection of scripts to interact with NEPSE related websites!',
    'long_description': '# NEPSE Utils\nCollection of scripts to interact with NEPSE related sites.\n## Installation\n`pip install nepseutils`\n\n\n### Class: MeroShare\n#### Constructor \\_\\_init__()\n- `name` Your name\n- `dpid` Depository Participants\n- `username` MeroShare Username\n- `password` MeroShare Password\n- `account` Bank Account Number\n- `dmat` DMAT Account Number\n- `crn` CRN Number\n- `pin` Transaction PIN\n- `capital_id` (Optional)\n\n#### _update_capital_list()\nUpdates list of capitals and saves a local copy.\n\n#### login()\nLogs into the account.\n\n#### logout()\nLogs out of the account\n\n#### get_applicable_issues()\nGets the list of currently open applicable issues.\n\n#### get_my_details()\nGets details of currently logged in acount\n\n#### get_application_status(share_id: str)\nGets the status of applied application.\n- `share_id` ID of applied issue\n\n#### apply(share_id: str, quantity: str)\nApplies for issues.\n- `share_id` ID of issue to apply\n- `quantity` Quantity to apply\n\n\n## Basic Usage:\n```\nfrom nepseutils import MeroShare\n\nif __name__=="__main__":\n    login_info = {\n            "name": "Jane Doe",\n            "username": "01111111",\n            "password": "janedoe1",\n            "dpid": "13700",\n            "dmat": "1301370001233333",\n            "crn": "01-R00122222",\n            "pin": "1234",\n            "account": "0075750611112222",\n    }\n\n    ms = MeroShare(**login_info)\n    ms.login()\n    ms.apply(share_id="342",quantity="10")\n    ms.logout()\n\n\n```\n\n## FAQ\n#### Why do I need to provide inputs other than Username, Password, and DPID?\nI haven\'t implemented the feature to extract client details from meroshare so you need to provide it. But it will be implemented in future releases.\n\n\n## Known Issues\nThese are known issues that I plan to fix in future versions:\n- Data types of some arguments like quantity and price is string\n- Retrying failed attempts is not implemented for some functions\n- Remove unnecessary inputs\n',
    'author': 'Daze',
    'author_email': 'dazehere@yandex.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/arpandaze/nepseutils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
