# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ml_caboodle', 'ml_caboodle.feature_selection']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.18,<2.0',
 'pandas>=1.1.0,<2.0.0',
 'scikit-learn>=0.24.0,<0.25.0',
 'tqdm>=4.41,<5.0']

setup_kwargs = {
    'name': 'ml-caboodle',
    'version': '0.2.1',
    'description': "All the stuff that doesn't have another home",
    'long_description': "# ML Caboodle\n\n* Author: Marius Helf \n  ([helfsmarius@gmail.com](mailto:helfsmarius@gmail.com))\n\nAll the stuff that doesn't have another home\n\n# Changelog\n\n## 0.2.1\n* fix: speculative rounds not removed when out of candidates\n\n## 0.2.0\n* feature: BackwardFeatureElimination\n* various bugfixes\n\n## 0.1.1\n* fix: ForwardFeatureSelection: return correct features when stopping\n  after speculative rounds.\n* improve logging output\n\n\n## 0.1.0\n\n* Initial release\n\n# License\n\n[MIT](https://choosealicense.com/licenses/mit)\n\n\n",
    'author': 'Marius Helf',
    'author_email': 'helfsmarius@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mariushelf/ml_caboodle',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
