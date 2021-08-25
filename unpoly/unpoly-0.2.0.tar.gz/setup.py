# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['unpoly', 'unpoly.contrib']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.2.0,<22.0.0']

extras_require = \
{':python_version < "3.8"': ['backports.cached_property>=1.0.1,<2.0.0']}

setup_kwargs = {
    'name': 'unpoly',
    'version': '0.2.0',
    'description': 'Framework agnostic implementation of the unpoly server-protocol.',
    'long_description': '[![version](https://img.shields.io/pypi/v/unpoly.svg)](https://pypi.org/project/unpoly)\n[![python versions](https://img.shields.io/pypi/pyversions/unpoly.svg)](https://pypi.org/project/unpoly)\n[![docs](https://img.shields.io/readthedocs/unpoly)](https://unpoly.readthedocs.io)\n[![pipeline status](https://gitlab.com/rocketduck/python-unpoly/badges/main/pipeline.svg)](https://gitlab.com/rocketduck/python-unpoly/-/commits/main)\n[![coverage report](https://gitlab.com/rocketduck/python-unpoly/badges/main/coverage.svg)](https://gitlab.com/rocketduck/python-unpoly/-/commits/main) \n\n# Unpoly\n\nUnpoly is a framework agnostic python library implementing the [Unpoly server protocol](https://unpoly.com/up.protocol).\n\n## Features\n\n* **Full protocol implementation**: The whole Unpoly server protocol is implemented and well tested.\n* **Django support**: Out of the box we currently ship a middleware for Django support.\n* **Easily extendable**: The library abstracts the actual HTTP stuff via adapters and can easily plugged into frameworks like Flask etc.\n\n## Download & Install\n\n```\npip install unpoly\n```\n\n### Usage with Django\n\nAdd `unpoly.contrib.django.UnpolyMiddleware` to your middlewares and then you can access `request.up`. Details can be found in the usage section of the [docs](https://unpoly.readthedocs.io/usage.html).\n\nExample usage:\n\n```py\ndef my_view(request):\n    if request.up: # Unpoly request\n        # Send an event down to unpoly\n        request.up.emit("test:event", {"event": "params"})\n        # ... and also clear the cache for certain paths\n        request.up.clear("/users/*")\n    else:\n        ...\n\ndef form_view(request):\n    form = MyForm(request.GET)\n    # When unpoly wants to validate a form it sends\n    # along X-Up-Validate which contains the field\n    # being validated.\n    if form.is_valid() and not request.up.validate:\n        form.save()\n    return render(request, "template.html", {"form": form})\n```\n\n### Usage with Flask etc\n\nSubclass `unpoly.adapter.BaseAdapter` and initialize `unpoly.Unpoly` with it for every request (see the [docs](https://unpoly.readthedocs.io/adapters.html) for details).',
    'author': 'Florian Apolloner',
    'author_email': 'florian@apolloner.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/rocketduck/python-unpoly',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<3.11',
}


setup(**setup_kwargs)
