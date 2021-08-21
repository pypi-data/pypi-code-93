# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mirai_extensions', 'mirai_extensions.trigger']

package_data = \
{'': ['*']}

install_requires = \
['yiri-mirai>=0.2.0']

setup_kwargs = {
    'name': 'yiri-mirai-trigger',
    'version': '0.3.0',
    'description': '[YiriMirai] 事件触发器：提供更多处理事件的方式。',
    'long_description': None,
    'author': '忘忧北萱草',
    'author_email': 'wybxc@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
