# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['netbox_plugin_gpon',
 'netbox_plugin_gpon.migrations',
 'netbox_plugin_gpon.netbox_plugin_gpon',
 'netbox_plugin_gpon.netbox_plugin_gpon.utilities',
 'netbox_plugin_gpon.netbox_plugin_gpon.views',
 'netbox_plugin_gpon.templates',
 'netbox_plugin_gpon.templates.netbox_plugin_gpon',
 'netbox_plugin_gpon.templates.netbox_plugin_gpon.generic',
 'netbox_plugin_gpon.templatetags']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'netbox-plugin-gpon',
    'version': '1.0.0',
    'description': 'This package adds GPON OLTs, ONTs, and Splitter logic and database operations to Netbox.',
    'long_description': None,
    'author': 'sutley',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MajesticFalcon/netbox_plugin_gpon',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
