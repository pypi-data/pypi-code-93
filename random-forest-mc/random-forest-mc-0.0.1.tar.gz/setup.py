# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['random_forest_mc']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.3.2']

setup_kwargs = {
    'name': 'random-forest-mc',
    'version': '0.0.1',
    'description': 'This project is about use Random Forest approach using a dynamic tree selection Monte Carlo based.',
    'long_description': '# Random Forest with Dyanmic Tree Selection Monte Carlo Based (RF-TSMC)\n![](forest.png)\n\n[![Python 3.7](https://img.shields.io/badge/Python-3.7-gree.svg)](https://www.python.org/downloads/release/python-370/)\n[![Python 3.8](https://img.shields.io/badge/Python-3.8-gree.svg)](https://www.python.org/downloads/release/python-380/)\n[![Python 3.9](https://img.shields.io/badge/Python-3.9-gree.svg)](https://www.python.org/downloads/release/python-390/)\n\n\nThis project is about use Random Forest approach using a dynamic tree selection Monte Carlo based. The first implementation is found in [2] (using Common Lisp).\n\n# References\n\n[2] [Laboratory of Decision Tree and Random Forest (`github/ysraell/random-forest-lab`)](https://github.com/ysraell/random-forest-lab). GitHub repository.\n\n[3] Credit Card Fraud Detection. Anonymized credit card transactions labeled as fraudulent or genuine. Kaggle. Access: <https://www.kaggle.com/mlg-ulb/creditcardfraud>.\n\n### Notes\n\n- Python requirements in `requirements.txt`. Better for Python `>=3.7`. Run the follow command inside this repository:\n\n```bash\n$ pip3 install -r requirements.txt --no-cache-dir\n```\n\n### Development Framework (optional)\n\n- [My data science Docker image](https://github.com/ysraell/my-ds).\n\nWith this image you can run all notebooks and scripts Python inside this repository.\n\n### TODO:\n\n- Implement the code.\n    - [Plus] Add a method to return the list of feaures and their degrees of importance.\n- Set Poetry and publish to PyPI.\n- Add parallel processing using or TQDM or csv2es style.\n',
    'author': 'Israel Oliveira',
    'author_email': 'israel.oliveira@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ysraell/random-forest-mc',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1',
}


setup(**setup_kwargs)
