# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['bottle_argsmap']
install_requires = \
['anyioc>=0.11.1,<0.12.0', 'bottle>=0.12.19,<0.13.0']

setup_kwargs = {
    'name': 'bottle-argsmap',
    'version': '0.1.1',
    'description': '',
    'long_description': "# bottle_argsmap\n\nAuto inject arguments via a `dict` like pattern.\n\n## Usage\n\n``` py\nfrom bottle import Bottle\nfrom bottle_argsmap import ArgsMapPlugin\n\napp = Bottle()\nplugin = try_install(app)\n\n# inject via singleton\nplugin.set_value('value', '1544')\n\n# or inject via factory, dynamic creation is allowed\n# e.g. you can to inject database connection from a database pool\nplugin.set_factory('value',\n    lambda param_name, route: ...,\n    context_manager=True,         # auto call `__exit__` on the value after responsed\n)\n\n# finally, inject it\n@app.get('/path')\ndef get_it(value): # value is injected\n    return dict(value=value)\n```\n\n## More\n\n`ArgsMapPlugin().ioc` is a instance of type `anyioc.ServiceProvider`, which means you can use all features from `anyioc`.\n",
    'author': 'Cologler',
    'author_email': 'skyoflw@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Cologler/bottle_argsmap-python',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
