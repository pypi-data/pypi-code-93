# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['char_pic']

package_data = \
{'': ['*']}

install_requires = \
['cowpy>=1.1.0,<2.0.0', 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'char-pic',
    'version': '0.1.3',
    'description': 'generate char pic demo.',
    'long_description': '这是一个生成字符图案的项目\n\n如下是使用说明：\n',
    'author': 'xiaodeng',
    'author_email': 'xiaodengteacher@qq.com',
    'maintainer': 'xiaodeng2',
    'maintainer_email': 'xiaodengteacher2@qq.com',
    'url': 'http://api.xiaodeng.site:8888/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
