# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['brython_dev']

package_data = \
{'': ['*']}

install_requires = \
['brython>=3.9.5,<4.0.0', 'flask>=2.0.1,<3.0.0', 'pyyaml>=5.4.1,<6.0.0']

entry_points = \
{'console_scripts': ['brython-dev = brython_dev.__main__:cli']}

setup_kwargs = {
    'name': 'brython-dev',
    'version': '0.7.0',
    'description': 'Brython developer tools',
    'long_description': '# Brython-dev\n\nBrython-dev is a Python library for developers in brython.\n\n## Installation\n\nUse the package manager [pip](https://pip.pypa.io/en/stable/) to install.\n\n```bash\npip install brython-dev\n```\n\n## Usage\n\nFor runserver\n\n```bash\npy -m brython_dev run\n```\n\n## Configuration\n\nThe configuration is in the filename `brython.yml`\n\n* **name**: String. The name of the proyect\n* **app**: String, Default: `app.py`. The python main filename\n* **template**: String, Default: `app.html`. The html main template\n* **console**: Boolean, Default: `true`. Enable he console in the navegator\n* **stylesheets**: List. A list whith extras stylesheets\n* **extensions**: Dict. A dict whith enable brython extensions\n  * **brython**: Boolean, Default: `true`. Enable the brython library\n  * **brython_stdlib**: Boolean, Default: `false`. Enable the brython stdlib library\n* **scripts**: List. A list whith extras scripts\n* **brython_options**: Dict. A dict whith brython options\n\n## License\n[MIT](https://choosealicense.com/licenses/mit/)',
    'author': 'Lorenzo Garcia Calzadilla',
    'author_email': 'lorenzogarciacalzadilla@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
