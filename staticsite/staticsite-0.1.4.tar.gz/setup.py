# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['staticsite']

package_data = \
{'': ['*']}

install_requires = \
['Flask-Minify>=0.23,<0.24', 'Jinja2>=2.11.2,<3.0.0', 'pyyaml>=5.3.1,<6.0.0']

setup_kwargs = {
    'name': 'staticsite',
    'version': '0.1.4',
    'description': 'Super simple Jinja2 based staticsite generator.',
    'long_description': "# StaticSite\n\nSuper simple static site builder.\n\n1. Create a folder called `src`.\n2. Put your Jinja templates there.\n3. Run `python -m staticsite build --src src --target www`\n4. Static site has been built and provided in `www` folder.\n5. Create a `staticsite.yaml` file to specify variables and plugins.\n\n```bash\nmkdir src\n\ncat << EOF >> src/.base.html\n<!doctype html>\n<html lang='en'>\n  <body>\n      <h1>Example</h1>\n    {% block content %}{% endblock %}\n  </body>\n</html>\nEOF\n\n\ncat << EOF >> src/index.html\n{% extends '.base.html' %}\n{% block content %}\nHi\n{% endblock %}\nEOF\n\n\npython -m staticsite build --target docs\n\n\ntree\n# .\n# ├── src\n# │\xa0\xa0 ├── .base.html  # Files starting with . are ignored\n# │\xa0\xa0 └── index.html\n# │\n# └── docs\n#  \xa0\xa0 ├── index.html\n```\n\n[Documentation](https://thesage21.github.io/staticsite/)\n",
    'author': 'arjoonn sharma',
    'author_email': 'arjoonn.94@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://thesage21.github.io/staticsite/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
