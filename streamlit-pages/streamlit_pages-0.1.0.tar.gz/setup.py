# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['streamlit_pages']

package_data = \
{'': ['*']}

install_requires = \
['streamlit>=0.84,<0.85']

setup_kwargs = {
    'name': 'streamlit-pages',
    'version': '0.1.0',
    'description': 'Addons like multipages for streamlit webapp',
    'long_description': '# streamlit_pages\n\n[![Python](https://img.shields.io/badge/python-3.6 3.7 3.8 3.9-blue)]()\n[![codecov](https://codecov.io/gh/bvenkatesh-ai/streamlit_pages/branch/main/graph/badge.svg)](https://codecov.io/gh/bvenkatesh-ai/streamlit_pages)\n[![Documentation Status](https://readthedocs.org/projects/streamlit_pages/badge/?version=latest)](https://streamlit_pages.readthedocs.io/en/latest/?badge=latest)\n\n\n## Installation\n\n```bash\n$ pip install -i https://test.pypi.org/simple/ streamlit_pages\n```\n\n## Features\n\n- Adding multiple pages to streamlit\n- Sharing specific pages\n\n## Dependencies\n\n- streamlit\n\n## Usage\n\n- TODO\n\n## Documentation\n\nThe official documentation is hosted on Read the Docs: https://streamlit_pages.readthedocs.io/en/latest/\n\n## Contributors\n\nWe welcome and recognize all contributions. You can see a list of current contributors in the [contributors tab](https://github.com/bvenkatesh-ai/streamlit_pages/graphs/contributors).\n\n### Credits\n\nThis package was created with Cookiecutter and the UBC-MDS/cookiecutter-ubc-mds project template, modified from the [pyOpenSci/cookiecutter-pyopensci](https://github.com/pyOpenSci/cookiecutter-pyopensci) project template and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage).\n',
    'author': 'Venkatesh Boddu',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bvenkatesh-ai/streamlit_pages',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
