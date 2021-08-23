# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['Simyan',
 'Simyan.issue',
 'Simyan.publisher',
 'Simyan.story_arc',
 'Simyan.volume']

package_data = \
{'': ['*']}

install_requires = \
['marshmallow>=3.13.0,<4.0.0',
 'ratelimit>=2.2.1,<3.0.0',
 'requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'simyan',
    'version': '0.2.0',
    'description': 'A Python wrapper for the Comicvine API.',
    'long_description': '# Simyan\n\n[![Version](https://img.shields.io/github/tag-pre/Buried-In-Code/Simyan.svg?label=version&style=flat-square)](https://github.com/Buried-In-Code/Simyan/releases)\n[![Issues](https://img.shields.io/github/issues/Buried-In-Code/Simyan.svg?style=flat-square)](https://github.com/Buried-In-Code/Simyan/issues)\n[![Contributors](https://img.shields.io/github/contributors/Buried-In-Code/Simyan.svg?style=flat-square)](https://github.com/Buried-In-Code/Simyan/graphs/contributors)\n[![License](https://img.shields.io/github/license/Buried-In-Code/Simyan.svg?style=flat-square)](https://opensource.org/licenses/MIT)\n\n[![Code Analysis](https://img.shields.io/github/workflow/status/Buried-In-Code/Simyan/Code-Analysis?label=Code-Analysis&logo=github&style=flat-square)](https://github.com/Buried-In-Code/Simyan/actions/workflows/code-analysis.yml)\n\nA [Python](https://www.python.org/) wrapper for the [Comicvine](https://comicvine.gamespot.com/api/) API.\n\n## Built Using\n\n- [Poetry: 1.1.7](https://python-poetry.org)\n- [Python: 3.9.6](https://www.python.org/)\n- [marshmallow: 3.13.0](https://pypi.org/project/marshmallow)\n- [requests: 2.26.0](https://pypi.org/project/requests)\n- [ratelimit: 2.2.1](https://pypi.org/project/ratelimit)\n\n## Installation\n\n### PyPI\n```bash\n$ pip install Simyan\n```\n\n## Example Usage\n```python\nfrom Simyan import api\n# Your config/secrets\nfrom config import comicvine_api_key\n\nsession = api(api_key=comicvine_api_key)\n\n# Search for Publisher\nresults = session.publisher_list(params={\'name\': \'DC Comics\'})\nfor publisher in results:\n    print(f"{publisher.id} | {publisher.name} - {publisher.site_url}")\n\n# Get details for a Volume\nresult = session.volume(_id=26266)\nprint(result.summary)\n```\n\n*There is a cache option to limit required calls to API*\n```python\nfrom Simyan import api, SqliteCache\n# Your config/secrets\nfrom config import comicvine_api_key\n\nsession = api(api_key=comicvine_api_key, cache=SqliteCache())\n\n# Get details for an Issue\nresult = session.issue(_id=189810)\nprint(f"{result.volume.name} #{result.issue_number}")\nprint(result.description)\n```\n\n## Socials\n\nBig thanks to [Mokkari](https://github.com/bpepple/mokkari) for the inspiration and template for this project.\n\n[![Discord | The DEV Environment](https://discordapp.com/api/guilds/618581423070117932/widget.png?style=banner2)](https://discord.gg/nqGMeGg)',
    'author': 'Buried-In-Code',
    'author_email': '6057651+Buried-In-Code@users.noreply.github.com',
    'maintainer': 'Buried-In-Code',
    'maintainer_email': '6057651+Buried-In-Code@users.noreply.github.com',
    'url': 'https://github.com/Buried-In-Code/Simyan',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
