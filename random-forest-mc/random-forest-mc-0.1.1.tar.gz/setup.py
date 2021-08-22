# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['random_forest_mc']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.2,<2.0.0',
 'pandas>=1.3.2,<2.0.0',
 'poetry-version>=0.1.5,<0.2.0',
 'tqdm>=4.62.1,<5.0.0']

setup_kwargs = {
    'name': 'random-forest-mc',
    'version': '0.1.1',
    'description': 'This project is about use Random Forest approach using a dynamic tree selection Monte Carlo based.',
    'long_description': '# Random Forest with Dynamic Tree Selection Monte Carlo Based (RF-TSMC)\n![](forest.png)\n\n[![Python 3.7](https://img.shields.io/badge/Python->=3.7-gree.svg)](https://www.python.org/downloads/release/python-370/)\n![](https://img.shields.io/badge/Coverage-100%25-green)\n\nThis project is about use Random Forest approach for *multiclass classification* using a dynamic tree selection Monte Carlo based. The first implementation is found in [2] (using Common Lisp).\n\n#### Development status: `Release Candidate`.\n\n## Install:\n\nInstall using `pip`:\n\n```bash\n$ pip3 install random-forest-mc\n```\n\nInstall from this repo:\n\n```bash\n$ git clone https://github.com/ysraell/random-forest-mc.git\n$ cd random-forest-mc\n$ pip3 install .\n```\n\n## Usage:\n\nExample of a full cycle using `titanic.csv`:\n\n```python\nimport numpy as np\nimport pandas as pd\n\nfrom random_forest_mc.model import RandomForestMC\nfrom random_forest_mc.utils import LoadDicts\n\ndicts = LoadDicts("tests/")\ndataset_dict = dicts.datasets_metadata\nds_name = "titanic"\nparams = dataset_dict[ds_name]\ndataset = (\n    pd.read_csv(params["csv_path"])[params["ds_cols"] + [params["target_col"]]]\n    .dropna()\n    .reset_index(drop=True)\n)\ndataset["Age"] = dataset["Age"].astype(np.uint8)\ndataset["SibSp"] = dataset["SibSp"].astype(np.uint8)\ndataset["Pclass"] = dataset["Pclass"].astype(str)\ndataset["Fare"] = dataset["Fare"].astype(np.uint32)\ncls = RandomForestMC(\n    n_trees=8, target_col=params["target_col"], max_discard_trees=4\n)\ncls.process_dataset(dataset)\ncls.fit()\ny_test = dataset[params["target_col"]].to_list()\ny_pred = cls.testForest(dataset)\naccuracy_hard = sum([v == p for v, p in zip(y_test, y_pred)]) / len(y_pred)\ny_pred = cls.testForest(dataset, soft_voting=True)\naccuracy_soft = sum([v == p for v, p in zip(y_test, y_pred)]) / len(y_pred)\n```\n\n### LoadDicts:\n\nLoadDicts works loading all `JSON` files inside a given path, creating an object helper to use this files as dictionaries.\n\nFor example:\n```python\n>>> from random_forest_mc.utils import LoadDicts\n>>> # JSONs: path/data.json, path/metdada.json\n>>> dicts = LoadDicts("path/")\n>>> # you have: dicts.data and dicts.metdada as dictionaries\n>>> # And a list of dictionaries loaded in:\n>>> dicts.List\n["data", "metdada"]\n```\n\n## Fundamentals:\n\n- Based on Random Forest method principles: ensemble of models (decision trees).\n\n- In bootstrap process:\n\n    - the data sampled ensure the balance between classes, for training and validation;\n\n    - the list of features used are randomly sampled (with random number of features and order).\n\n- For each tree:\n\n    - fallowing the sequence of a given list of features, the data is splited half/half based on meadian value;\n\n    - the splitting process ends when the samples have one only class;\n\n    - validation process based on dynamic threshold can discard the tree.\n\n- For use the forest:\n\n    - all trees predictions are combined as a vote;\n\n    - it is possible to use soft or hard-voting.\n\n- Positive side-effects:\n\n    - possible more generalization caused by the combination of overfitted trees, each tree is highly specialized in a smallest and different set of feature;\n\n    - robustness for unbalanced and missing data, in case of missing data, the feature could be skipped without degrade the optimization process;\n\n    - in prediction process, a missing value could be dealt with a tree replication considering the two possible paths;\n\n    - the survived trees have a potential information about feature importance.\n\n### References\n\n[2] [Laboratory of Decision Tree and Random Forest (`github/ysraell/random-forest-lab`)](https://github.com/ysraell/random-forest-lab). GitHub repository.\n\n[3] Credit Card Fraud Detection. Anonymized credit card transactions labeled as fraudulent or genuine. Kaggle. Access: <https://www.kaggle.com/mlg-ulb/creditcardfraud>.\n\n### Development Framework (optional)\n\n- [My data science Docker image](https://github.com/ysraell/my-ds).\n\nWith this image you can run all notebooks and scripts Python inside this repository.\n\n### TODO v0.2:\n\n- Add parallel processing using or TQDM or csv2es style.\n- Prediction with missing values: `useTree` must be functional and branching when missing value, combining classes at leaves with their probabilities.\n- [Plus] Add a method to return the list of feaures and their degrees of importance.\n\n### TODO v0.3:\n\n- Docstring.\n',
    'author': 'Israel Oliveira',
    'author_email': 'israel.oliveira@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ysraell/random-forest-mc',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.11',
}


setup(**setup_kwargs)
