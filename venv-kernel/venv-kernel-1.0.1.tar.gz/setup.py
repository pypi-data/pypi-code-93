# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['venv_kernel']

package_data = \
{'': ['*']}

install_requires = \
['ipykernel>=6.2,<7.0', 'rich>=10.7,<11.0', 'typer>=0.3.2,<0.4.0']

entry_points = \
{'console_scripts': ['venv-kernel = venv_kernel.kernel_tool:app']}

setup_kwargs = {
    'name': 'venv-kernel',
    'version': '1.0.1',
    'description': 'Create a custom jupyter kernel for your venv.',
    'long_description': '# venv-kernel #\n\n[![PyPI - latest version](https://img.shields.io/pypi/v/venv-kernel.svg)](https://pypi.org/project/venv-kernel/)\n[![PyPI - License](https://img.shields.io/pypi/l/venv-kernel.svg)](https://pypi.org/project/venv-kernel/)\n[![PyPI - supported Python versions](https://img.shields.io/pypi/pyversions/venv-kernel.svg)](https://pypi.org/project/venv-kernel/)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/venv-kernel)](https://pypi.org/project/venv-kernel/)\n\n## Summary ##\n\nThis package creates jupyter kernels for the `venv` it is installed\nin.\n\n## Use-case scenario ##\n\nYou maintain multiple virtual environments via python\'s `venv`. You\nwant to be able to switch between them from within a _single_ jupyter\ninstallation. How do you do this?\n\nYou need a (user-) global jupyter installation. The recommended\napproach for that is to use `pipx` to install jupyter as a standalone\ntool. Jupyter can handle multiple different kernels, even for the same\npython version, and they are easily maintained with the `jupyter\nkernelspec` command. The only nuissance is to create and install the\nkernel.json files manually for each venv. That\'s where `venv-kernel`\ncomes in.\n\n## Suggested workflow ##\n\n### One-time setup ###\n\nIt is recommended to maintain your python versions with `pyenv` and\njupyter with `pipx`. Both of these packages can be installed with the\nusual package managers such as `apt-get` or `brew`.\n\nSpecifically, install and temporarily activate a recent python version\nwith pyenv, e.g., via\n```\npyenv install 3.9.10\npyenv shell 3.9.10\n```\nThen install jupyter using pipx as per\n```\npipx install --install-deps notebook jupyter jupyter_contrib_nbextensions\n```\nwhich places it in its own virtual environment, all managed by\npipx. You can call jupyter from the command line now.\n\n### Install a custom kernel for a VENV ###\n\nEvery time you want to add a custom virtual environment as a kernel\noption to your jupyter notebook server, follow these steps:\n\n1. If you haven\'t done so yet, create and activate the venv as per usual, e.g., via\n    ```bash\n    pyenv shell 3.10 # we want to use this particular python version\n    pip -m venv .venv\n    . .venv/bin/activate\n    pip install --upgrade pip\n    pip install <list of packages here> or pip install -r requirements.txt\n    ```\n2. Install venv-kernel as per\n    ```bash\n    pip install venv-kernel\n    ```\n3. Create and install the custom jupyter kernel\n    ```bash\n    venv-kernel install --name "MyProject" --description "Virtual Environment for MyProject using Python 3.10"\n    ```\n   Here the `--name` and `--description` are optional and default\n   to the direcory name of the virtual environment.\n4. Start/restart your jupyter notebook server. You should now see the\n   kernel "MyProject", which uses the Python version of your virtual\n   environment and has access to all the packages installed in it.\n    \n### Removal ###\n    \nIf for any reason you want to uninstall a kernel created by this\npackage, you can simply do so using the commands\n```bash\njupyter kernelspec list\n```\nto identify the kernel in question\nand then delete it via \n```bash\njupyter kernelspec remove\n```\n\nIf you are within a virtualenv that has `venv-kernel` installed, you\ncan also use\n```bash\nvenv-kernel list\n```\nto see if there\'s currently a kernel installed that corresponds to the current venv, and \n```bash\nvenv-kernel clean\n```\nto remove it.\n\n## Similar packages ##\n    \nThere are other packages that provide similar or related\nfunctionality, and these may or may not serve your purposes better\nthan this package, which is designed solely to meet the author\'s\nneeds. These packages include:\n\n- [callisto](https://pypi.org/project/callisto/): Create jupyter kernels from virtual environments\n- [envkernel](https://pypi.org/project/envkernel/): Jupyter kernels manipulation and in other environments (docker, Lmod, etc.)\n- [ssh-ipykernel](https://pypi.org/project/ssh-ipykernel/): A remote jupyter ipykernel via ssh\n    \n## MIT License ##\n\nCopyright 2021 Björn Rüffer\n\nPermission is hereby granted, free of charge, to any person obtaining\na copy of this software and associated documentation files (the\n"Software"), to deal in the Software without restriction, including\nwithout limitation the rights to use, copy, modify, merge, publish,\ndistribute, sublicense, and/or sell copies of the Software, and to\npermit persons to whom the Software is furnished to do so, subject to\nthe following conditions:\n\nThe above copyright notice and this permission notice shall be\nincluded in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,\nEXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF\nMERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND\nNONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE\nLIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION\nOF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION\nWITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n\n\n\n    \n',
    'author': 'Björn Rüffer',
    'author_email': 'bjoern@rueffer.info',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bjoseru/venv-kernel',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
