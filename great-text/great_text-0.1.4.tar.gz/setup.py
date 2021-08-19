# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['great_text']

package_data = \
{'': ['*']}

install_requires = \
['pyfiglet>=0.8.post1,<0.9', 'termcolor>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'great-text',
    'version': '0.1.4',
    'description': 'Add font and color to your Python text.',
    'long_description': '# Great Text \n\nThis package enables you to print great text like below\n![image](https://github.com/DeepakDarkiee/great-text/blob/master/great.png?raw=True).\n\n\n\ngreat-text requires [Python](https://www.python.org/downloads/release/python-395/) v8+ to run.\n\n\nTo install this package, use \n\n```bash\npip install great-text\n```\n\n\n\n## RUN\n\nWant to contribute? Great!\n\nOpen your favorite Terminal and run these commands.\n\nFirst Tab:\n\n```sh\ntouch example.py\n```\n\nOpen your favorite text editor and write \n\n```sh\nfrom great_text import great_text\n```\n\ncall the function great-text with arguments given bellow \n```sh\ngreat_text("Hello", "isometric2", "red")\n```\nthe code will look like this\n\n```sh\nfrom great_text import great_text\n\ngreat_text("Hello", "isometric2", "red")\n\n```\n\n\n> Note: `You can change text ,color and fonts` \n\nNow RUN\n\n```sh\npython example.py\n```\n\n## License\n\nMIT\n\n**Free Software, Hell Yeah!**\n## Author \n[Deepak Patidar](https://github.com/DeepakDarkiee/great-text)\n\n\n',
    'author': 'Deepak Patidar',
    'author_email': 'info.deepakpatidar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeepakDarkiee/great-text.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
