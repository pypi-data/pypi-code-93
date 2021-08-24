# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_salesforce_oauth']

package_data = \
{'': ['*']}

install_requires = \
['django>=3.0.7,<4.0.0', 'requests>=2.24.0,<3.0.0']

setup_kwargs = {
    'name': 'django-salesforce-oauth',
    'version': '0.3.3',
    'description': 'Simple package for creating and signing users into your Django site using Salesforce as an OAuth provider',
    'long_description': '# Quick start\n\nAssuming you\'ve already configured an app in your Salesforce instance to serve\nas an OAuth provider, the following should get you up and running.\n\n## Install\n\n`pip install django-salesforce-oauth`\n\n## Settings\n\nAdd the app to your `INSTALLED_APPS` in your django settings (`settings.py`):\n\n```python\nINSTALLED_APPS = [\n    # ...\n    "django_salesforce_oauth",\n]\n```\n\nAdd the following required variables to your `settings.py`:\n\n```python\nSCOPES = "YOUR SCOPES"  # space delimited, e.g., "id api refresh_token"\nSFDC_CONSUMER_KEY = "YOUR KEY"\nSFDC_CONSUMER_SECRET = "YOUR SECRET"\nOAUTH_REDIRECT_URI = "{YOUR DOMAIN}/oauth/callback/"\n\n# Optional, but Django provides a default you likely don\'t want\nLOGIN_REDIRECT_URL = "/"\n```\n\n## Urls\n\nAdd `django-salesforce-oauth`\'s urls to your main `urls.py`.\n\n```python\nfrom django.urls import path, include\n\nurlpatterns = [\n    # ...\n    path("oauth/", include("django_salesforce_oauth.urls")),\n]\n```\n\nThen redirect sign-in requests to the `oauth` namespace.\n\n### View example\n\n```python\nfrom django.shortcuts import redirect\n\ndef your_view(request):\n    return redirect("oauth")  # or "oauth-sandbox"\n```\n\n### Template example\n\n```html\n<a href="{% url \'oauth\' %}" class="btn btn-primary">Login</a>\n```\n\n# Advanced usage\n\n## Custom callback\n\nYou likely will want to customize what happens after the OAuth flow is complete instead of simply\ngetting or creating a user. This can be done by specifying the following in your `settings.py`.\n\n```python\nCUSTOM_CALLBACK = "path.to.module.your_callback_function"\n```\n\n`your_callback_function` must accept the following two arguments:\n\n1. the request object (useful in case you want to handle redirection yourself)\n2. the OAuth object (contains all token and user data)\n\nIf you do not return a redirect from `your_callback_function`, it\'s expected it will return\na user object. In this case the user will then be signed in and redirected to\n`settings.LOGIN_REDIRECT_URL` (which you\'ll most likely want to set in your `settings.py`).\n\n### Customizing the callback URI\n\nBy default the view behind the `oauth-callback` namespace, specified in the `django_salesforce_oauth`\'s app\'s `urls.py`, is what needs to match `settings.OAUTH_REDIRECT_URI`.\nBut this can be customized by pointing it to some other url and registering the view wherever\nyou\'d like it declared.\n\n```python\n# urls.py\n\nfrom django_salesforce_oauth.views import oauth_callback\n\nurlpatterns = [\n    # ...\n    # pass {"domain": "test"} to use a sandbox\n    path("my/custom/url", oauth_callback, {"domain": "login"}, name="custom-oauth-callback"),\n]\n```\n\n# Example project\n\nThe example project provides a full example of how to use this package,\nbut since it\'s an integration, there\'s a few steps to actually running it.\n\n## SFDC\n\nConfigure a SFDC OAuth app with which you can OAuth against.\n\n## .env\n\nPlace a `.env` file inside the `project` folder that contains the following keys\nfrom the OAuth app you configured above:\n\n```\nSFDC_CONSUMER_KEY=some_key\nSFDC_CONSUMER_SECRET=secret_stuff\n```\n\n## django\n\nrun migrations and start the server!\n\n---\n\nThis project uses [poetry](https://python-poetry.org/) for dependency management\nand packaging.\n',
    'author': 'Alex Drozd',
    'author_email': 'drozdster@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/brno32/django-salesforce-oauth',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
