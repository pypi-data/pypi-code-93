# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['genderclf']

package_data = \
{'': ['*'], 'genderclf': ['models/*']}

install_requires = \
['joblib>=0.14.0,<0.15.0', 'scikit-learn>=0.22.0,<0.23.0']

setup_kwargs = {
    'name': 'genderclf',
    'version': '0.0.1',
    'description': 'Gender Classifier ML Package for classifying gender using firstname',
    'long_description': '## GenderClassifier Tool\n+ For classifying gender of individuals using their first names\n\n### Installation\n```bash\npip install genderclf\n```\n\n### Usage\n#### Basic usage\n```python\n>>> from genderclf import GenderClassifier\n>>> g = GenderClassifier()\n>>> g.name = \'Hemant\'\n>>> g.predict()\n```\n\n#### Loading Different Models\n```python\n>>> from genderclf import GenderClassifier\n>>> g = GenderClassifier()\n>>> g.name = \'Hansa\'\n>>> g.load(\'logit\')\n>>> g.predict()\n```\n\n#### Using the Classify Method\n```python\n>>> from genderclf import GenderClassifier\n>>> g = GenderClassifier()\n>>> g.load(\'nb\')\n>>> g.classify("Hemant")\n```\n\n#### Check Gender\n```python\n>>> from genderclf import GenderClassifier\n>>> g = GenderClassifier()\n>>> g.is_male("Hemant")\n```\n\n```python\n>>> from genderclf import GenderClassifier\n>>> g = GenderClassifier()\n>>> g.is_female("Hansa")\n```\n\n#### Requirements\n+ Joblib\n+ Scikit-learn\n\n#### Maintainer\n+ Ankit Hemant Lade(ankitlade12@gmail.com)\n',
    'author': 'Ankit Hemant Lade',
    'author_email': 'ankitlade12@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ankitlade12/genderclf',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
