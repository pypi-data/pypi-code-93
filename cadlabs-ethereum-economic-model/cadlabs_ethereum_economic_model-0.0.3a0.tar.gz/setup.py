# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'package'}

packages = \
['.ipynb_checkpoints',
 'cadlabs_ethereum_economic_model',
 'cadlabs_ethereum_economic_model.experiments',
 'cadlabs_ethereum_economic_model.model',
 'experiments',
 'experiments.notebooks',
 'experiments.notebooks.simulation_profiling',
 'experiments.notebooks.visualizations',
 'experiments.templates',
 'model',
 'model.parts',
 'model.parts.utils',
 'package',
 'package.cadlabs_ethereum_economic_model',
 'package.cadlabs_ethereum_economic_model.experiments',
 'package.cadlabs_ethereum_economic_model.model']

package_data = \
{'': ['*'],
 'experiments': ['outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_1a.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_1a.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_1a.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_1a.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_1a.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_1b.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_1b.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_1b.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_1b.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_1b.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_2.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_2.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_2.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_2.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_2.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_3a.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_3a.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_3a.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_3a.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_3a.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_3b.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_3b.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_3b.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_3b.png',
                 'outputs/hoban_borgers_economic_model/experiment_model_validation_scenario_3b.png',
                 'outputs/validator_environment_yield_contour.png'],
 'experiments.notebooks.visualizations': ['assets/*']}

install_requires = \
['cadCAD-tools==0.0.1.4',
 'diskcache==5.2.1',
 'ipython-autotime==0.3.1',
 'ipywidgets==7.6.3',
 'jupyter-dash==0.4.0',
 'matplotlib==3.3.4',
 'notebook==6.3.0',
 'numpy==1.21.2',
 'plotly==4.14.3',
 'radcad==0.8.0',
 'requests>=2.26.0,<3.0.0',
 'scipy>=1.7.1,<2.0.0',
 'stochastic==0.6.0',
 'tqdm==4.61.0',
 'typing-extensions==3.7.4.3']

setup_kwargs = {
    'name': 'cadlabs-ethereum-economic-model',
    'version': '0.0.3a0',
    'description': '',
    'long_description': None,
    'author': 'BenSchZA',
    'author_email': 'BenSchZA@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
