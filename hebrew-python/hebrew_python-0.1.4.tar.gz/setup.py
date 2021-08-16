# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hebrew_python']

package_data = \
{'': ['*']}

install_requires = \
['friendly-traceback>=0.4.36,<0.5.0',
 'friendly>=0.4.14,<0.5.0',
 'ideas>=0.0.22,<0.0.23']

entry_points = \
{'console_scripts': ['hepy = hebrew_python.__main__:main']}

setup_kwargs = {
    'name': 'hebrew-python',
    'version': '0.1.4',
    'description': 'write python in Hebrew',
    'long_description': '# hebrew-python\nhebrew-python is a python library (with commandline utities) for programming python in Hebrew.\n(Yes, it is really possible!)\n\nhebrew-python\nruns in Python 3.6+ (because `ideas` runs in Python 3.6+)\n\n\nAfter downloading this library you can write a script like:\n```python\nמתוך בנוי.אקראי יבא מספר_אקראי\nמשתנה_כלשהו = מספר_אקראי(1,9)\nהראה(משתנה_כלשהו)\n```\nName the file `something.hepy` and run it with `hepy something.hepy`.\n\nYou can also import other `.hepy` and `.py` files from the main file:\n```Python\nיבא something\n```\n\n## Installing\nTo install with pip\ntype in terminal:\n```\n(sudo) pip install hebrew-python\n```\nThis will create the commandline script:`hepy`\n\n## Usage\nYou can run hepy files with `hepy <file>`\n\nYou can start Hebrew Python console with just `hepy`\n\n## `.hepy` file syntax\n`.hepy` file supports hebrew python syntax (syntax with keywords like `יבא`(import)  \nand functions like `הראה` (print))\nin additional to normal python syntax\n\n## Use from normal python file/repl\nYou can use as library:\n\nto import `.hepy` files into your `.py` file:\n```python\nfrom hebrew_python import create_hook\ncreate_hook(run_module=False, console=False) # without running main module or starting repl\nimport hepy_module # now you can import .hepy files\n```\n\nor to start repl from normal repl:\n```python\nfrom hebrew_python import create_hook\ncreate_hook(run_module=True, console=True) # *with* starting repl\n```\n## jupyter/ipython\n`hebrew-python` support [jupyter](https://jupyter.org) and [ipython](https://ipython.org/) intercative console by ipython extension. to use:\n\ninstall jupyter-notebook by : `pip install notebook`  \nstart jupyter-notebook by : `jupyter notebook`.\nthen create new python3 by the new button.\n\non the first cell enter the text `%load_ext hebrew_python` and pross contoll+enter.\n\nand then you can write hebrew-python in all notebook\n\n## Dependencies\nhebrew-python depends on the python libraries:\n<!--* [friendly](https://github.com/aroberge/friendly) - for more friendly traceback (friendly doesn\'t have translation to Hebrew yet, so currently it\'s using [my fork](https://github.com/matan-h/friendly) with my own translation to Hebrew. Will merge soon).-->\n\n[friendly](https://github.com/aroberge/friendly) - for more friendly english traceback\n\n* [ideas](https://github.com/aroberge/ideas) - most of this library is built on this project. It support easy creation of import hooks and it has a [simple example](https://github.com/aroberge/ideas/blob/master/ideas/examples/french.py) for replacing keywords to French keywords\n\n## Contribute\nOn all errors, problems or suggestions please open a [github issue](https://github.com/matan-h/ddebug/issues)  \n\nIf you found this library useful, it would be great if you could buy me a coffee:  \n\n<a href="https://www.buymeacoffee.com/matanh" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee" height="47" width="200"></a>\n\n## Author\nmatan h\n\n## License\nThis project is licensed under the [BSD-4 License](https://spdx.org/licenses/BSD-4-Clause.html).\n',
    'author': 'matan h',
    'author_email': 'matan.honig2@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/matan-h/hebrew-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
