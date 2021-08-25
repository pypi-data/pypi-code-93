# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['skip_ssg']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.1,<4.0.0',
 'Markdown>=3.3.4,<4.0.0',
 'Pygments>=2.9.0,<3.0.0',
 'arrow>=1.1.1,<2.0.0',
 'gitignore-parser>=0.0.8,<0.0.9',
 'python-frontmatter>=1.0.0,<2.0.0',
 'watchgod>=0.7,<0.8']

entry_points = \
{'console_scripts': ['skip = skip_ssg.skip:main']}

setup_kwargs = {
    'name': 'skip-ssg',
    'version': '0.1.10',
    'description': 'A simple python-based static site generator',
    'long_description': "# Skip\n\nSkip is a Python-based data-forward static site generator inspired by [Eleventy](https://11ty.dev)\n\n## Why should I use Skip?\n\n- You like Python and the Jinja2 templating engine\n- You want a simple static site generator that makes no assumptions about how your project should be structured\n- You want to use data files, including dynamically computed data (like reading from a database or API)\n\n## Quickstart\n\n``` bash\npip install skip-ssg\necho '# Hello World' > index.md\nskip\n```\n\nTo see more, check out the [documentation](skip.harryeldridge.com)\n",
    'author': 'Harry Eldridge',
    'author_email': 'heldridge@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/heldridge/skip',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
