# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['djangofobi_email_router']

package_data = \
{'': ['*'],
 'djangofobi_email_router': ['locale/fr/LC_MESSAGES/*',
                             'templates/email_router/*']}

install_requires = \
['Django>=1.11', 'django-fobi>=0.17.0,<0.18.0']

setup_kwargs = {
    'name': 'djangofobi-email-router',
    'version': '1.0.2',
    'description': 'A django-fobi handler plugin to send the content of a form to different e-mails addresses, depending on a value of a form field.',
    'long_description': '# Django fobi email router\n\nA django-fobi handler plugin to send the content of a form to different e-mails addresses, depending on a value of a form field.\n\n## Install\n\n1. Install module\n   ```bash\n   python3 -m pip install djangofobi-email-router\n   ```\n\n2. Add it to your INSTALLED_APPS\n   ```\n   "djangofobi_email_router",\n   ```\n\n3. Create a fobi form with at least one choice field (select or radio)\n4. Add an `E-mail router` handler, fill in the name of your choice field and the e-mails corresponding to the different possible values\n\n### Requirements\n\n* `django-fobi`\n\n## Screenshot\n\n![preview djangofobi-email-router](https://gitlab.com/kapt/open-source/djangofobi-email-router/-/raw/main/preview.png)\n',
    'author': 'KAPT dev team',
    'author_email': 'dev@kapt.mobi',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
