# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['turbo', 'turbo.templatetags']

package_data = \
{'': ['*'], 'turbo': ['static/turbo/js/*', 'templates/turbo/*']}

install_requires = \
['Django>=3.0.0', 'channels>=2.0.0']

setup_kwargs = {
    'name': 'turbo-django',
    'version': '0.2.3',
    'description': 'Integrate Hotwire Turbo with Django allowing for a Python-driven dynamic web experience.',
    'long_description': '[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fhotwire-django%2Fturbo-django%2Fbadge%3Fref%3Dmain&style=flat)](https://actions-badge.atrox.dev/hotwire-django/turbo-django/goto?ref=main)\n[![Documentation Status](https://readthedocs.org/projects/turbo-django/badge/?version=latest)](https://turbo-django.readthedocs.io/en/latest/?badge=latest)\n[![Issues](https://img.shields.io/github/issues/hotwire-django/turbo-django)](https://img.shields.io/github/issues/hotwire-django/turbo-django)\n[![Twitter](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2FDjangoHotwire)](https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2Fhotwire-django%2Fturbo-django)\n\n# Turbo for Django\n\n\nIntegrate [Hotwire Turbo](https://turbo.hotwired.dev/) with Django with ease.\n\n\n## Requirements\n\n- Python 3.6+\n- Django 3.1+\n- Channels 3.0+ _(Optional for Turbo Frames, but needed for Turbo Stream support)_\n\n##Installation\n\nTurbo Django is available on PyPI - to install it, just run:\n\n    pip install turbo-django\n\n_Note: Both Hotwire and this library are still in beta development and may introduce breaking API changes between releases.  It is advised to pin the library to a specific version during install._\n\n## Quickstart\nWant to see Hotwire in action? Here\'s a simple broadcast that can be setup in less than a minute.\n\n**The basics:**\n\n* A web page subscribes to a specific broadcast name.\n\n* A view sends a rendered template to all subscribed pages telling the page where to position the new content.\n\n\n### Example\n\nFirst, create a view that takes a broadcast name.\n\n\n```python\nfrom django.urls import path\nfrom django.views.generic import TemplateView\n\nurlpatterns = [\n    path(\'quickstart/\', TemplateView.as_view(template_name=\'broadcast_example.html\'))\n]\n```\n\n```html\n# broadcast_example.html\n\n{% load turbo_streams %}\n<!DOCTYPE html>\n<html lang="en">\n<head>\n    {% include "turbo/head.html" %}\n</head>\n<body>\n    {% turbo_subscribe \'broadcast_name\' %}\n\n    <p class="broadcast_box_class" id="broadcast_box">Placeholder for broadcast</p>\n</body>\n</html>\n```\n\nNow run ``./manage.py shell``.  Create a Turbo object that references the broadcast name.  Tell the object to render a ``TurboRender`` object from the string, and then broadcast a command to `update` the inside of the element with id `broadcast_box` on all subscribed pages.\n\n```python\nfrom turbo import Turbo\nfrom datetime import datetime\n\nTurbo(\'broadcast_name\').render_from_string(\n    f"{datetime.now()}: This is a broadcast."\n).update(id="broadcast_box")\n```\n\nWith the `quickstart/` path open in a browser window, watch as the broadcast pushes messages to the page.\n\nNow change `.update()` to `.append()` and resend the broadcast a few times. Notice you do not have to reload the page to get this modified behavior.\n\nExcited to learn more?  Be sure to walk through the [tutorial](https://turbo-django.readthedocs.io/en/latest/index.html) and read more about what Turbo can do for you.\n\n## Documentation\nRead the [full documentation](https://turbo-django.readthedocs.io/en/latest/index.html) at readthedocs.io.\n\n\n## Contribute\n\nDiscussions about a Django/Hotwire integration are happening on the [Hotwire forum](https://discuss.hotwired.dev/t/django-backend-support-for-hotwire/1570). And on Slack, which you can join by [clicking here!](https://join.slack.com/t/pragmaticmindsgruppe/shared_invite/zt-kl0e0plt-uXGQ1PUt5yRohLNYcVvhhQ)\n\nAs this new magic is discovered, you can expect to see a few repositories with experiments and demos appear in [@hotwire-django](https://github.com/hotwire-django). If you too are experimenting, we encourage you to ask for write access to the GitHub organization and to publish your work in a @hotwire-django repository.\n\n\n## License\n\nTurbo-Django is released under the [MIT License](https://opensource.org/licenses/MIT) to keep compatibility with the Hotwire project.\n\nIf you submit a pull request. Remember to add yourself to `CONTRIBUTORS.md`!\n',
    'author': 'Nikita Marchant',
    'author_email': 'C4ptainCrunch@github-username.x',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
