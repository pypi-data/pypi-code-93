# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['requests_iam_session']

package_data = \
{'': ['*']}

install_requires = \
['aws-requests-auth>=0.4,<0.5',
 'boto3>=1.16,<2.0',
 'requests-toolbelt>=0.9,<0.10',
 'requests>=2.0,<3.0']

setup_kwargs = {
    'name': 'requests-iam-session',
    'version': '0.2.0',
    'description': 'AWSSession class that extends BaseUrlSession from requests and automatically authenticates through IAM.',
    'long_description': '# requests-iam-session\n\nAWSSession class that extends [BaseUrlSession](https://toolbelt.readthedocs.io/en/latest/sessions.html) from [requests](https://docs.python-requests.org/en/master/) and automatically authenticates through IAM. \n\n## Installation\n\n```\npoetry add requests-iam-session\n```\n\n## Usage example\n```python\nfrom requests_iam_session import AWSSession\n\nsession = AWSSession("https://example.com/")\nresponse = session.get("/users/1")\n\nprint(response.json())\n```\n',
    'author': 'Epsy Engineering',
    'author_email': 'engineering@epsyhealth.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/epsyhealth/requests-iam-session',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
