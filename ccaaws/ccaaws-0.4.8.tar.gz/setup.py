# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ccaaws']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.11.5,<2.0.0', 'ccalogging>=0.3.3,<0.4.0', 'ccautils>=0.4.0,<0.5.0']

setup_kwargs = {
    'name': 'ccaaws',
    'version': '0.4.8',
    'description': 'AWS boto3 objects for python',
    'long_description': '# ccaaws\n\nPython objects wrapped around [boto3](https://github.com/boto/boto3)\n\n## botosession.py\n\nBase class inherited by all the others.  Manages connections to AWS via\naccess keys or profiles.\n\n## cfnclient.py\n\nCloudFormation client\n\n## cwclient.py\n\nCloudWatch client\n\n## iamclient.py\n\nAccess to IAM functions - mainly for user access key management.\n\nCan raise an `AccessKeyError` exception on failure.\n\n```\nfrom ccaaws.iamclient import IamClient\n\niam = IamClient("iam.user")\nnewkey = iam.rotateKeys()\n```\n\n## paramstore.py\n\nSSM ParameterStore client\n\n[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )\n',
    'author': 'ccdale',
    'author_email': 'chris.charles.allison+ccaaws@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
