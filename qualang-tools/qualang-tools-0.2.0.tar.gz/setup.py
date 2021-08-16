# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qualang_tools', 'qualang_tools.bakery']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.2,<4.0.0', 'numpy>=1.20.3,<2.0.0', 'pandas>=1.2.4,<2.0.0']

setup_kwargs = {
    'name': 'qualang-tools',
    'version': '0.2.0',
    'description': 'The qualang_tools package includes tools for writing QUA programs in Python.',
    'long_description': '# py-qua-tools\n\nThe qualang_tools package includes tools for writing QUA programs in Python. \n\nThe first included tool is the baking tool for working with waveforms at a 1ns resolution. \n\n## installation\n\nInstall the current version using `pip`\n\n```\npip install qualang-tools\n```\n\n## usage\n\nExamples for 1-qubit randomized benchamrking or cross-entropy benchmark (XEB) can be found in the examples folder of the [py-qua-tools repository](https://github.com/qua-platform/py-qua-tools/)\n\n\n',
    'author': 'QM',
    'author_email': 'qua-libs@quantum-machines.co',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qua-platform/py-qua-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
