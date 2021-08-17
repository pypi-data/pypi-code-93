# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fulmo',
 'fulmo.callbacks',
 'fulmo.core',
 'fulmo.datasets',
 'fulmo.losses',
 'fulmo.metrics',
 'fulmo.models',
 'fulmo.models.cv',
 'fulmo.models.layers',
 'fulmo.models.layers.activation',
 'fulmo.models.layers.pooling',
 'fulmo.optimizers',
 'fulmo.readers',
 'fulmo.samplers',
 'fulmo.schedulers',
 'fulmo.utils']

package_data = \
{'': ['*']}

install_requires = \
['albumentations>=0.5.2,<1.1.0',
 'hydra-core==1.1.0',
 'imageio>=2.9.0,<3.0.0',
 'kornia>=0.5.4,<0.6.0',
 'nptyping>=1.4.1,<2.0.0',
 'pandas>=1.2.3,<2.0.0',
 'python-dotenv>=0.17.1,<0.20.0',
 'pytorch-lightning>=1.3.6,<2.0.0',
 'rich>=9.8.2,<11.0.0',
 'scikit-image>=0.18.1,<0.19.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'timm>=0.4.5,<0.5.0',
 'torch-optimizer>=0.1.0,<0.2.0']

setup_kwargs = {
    'name': 'fulmo',
    'version': '0.3.1',
    'description': 'Template to start your deep learning project based on `PyTorchLightning` for rapid prototyping.',
    'long_description': '<div align="center">\n\n[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/jexio/fulmo?logo=github)](https://github.com/jexio/fulmo/releases)\n[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9-blue?logo=python)](https://www.python.org/)\n[![Tests](https://github.com/jexio/fulmo/workflows/tests/badge.svg)](https://github.com/jexio/fulmo/actions?workflow=tests)\n[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square)](https://conventionalcommits.org)\n\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)\n\n</div>\n\n# fulmo\n\nTemplate to start your deep learning project based on `PyTorchLightning` for rapid prototyping.\n\n**Contents**\n- [fulmo](#fulmo)\n  - [Why Lightning + Hydra + Albumentations?](#why-lightning--hydra--albumentations)\n  - [Features](#features)\n  - [Project Structure](#project-structure)\n  - [Workflow](#workflow)\n  - [Experiment Tracking](#experiment-tracking)\n  - [Quick start](#quickstart)\n  - [Todo](#todo)\n  - [Credits](#credits)\n<br>\n    \n## Why Lightning + Hydra + Albumentations?\n- [PyTorch Lightning][PyTorchLightning/pytorch-lightning] provides great abstractions for well structured ML code and advanced features like checkpointing, gradient accumulation, distributed training, etc.\n- [Hydra][facebookresearch/hydra] provides convenient way to manage experiment configurations and advanced features like overriding any config parameter from command line, scheduling execution of many runs, etc.\n- [Albumentations][albumentations-team/albumentations] (**Optional**) provides many image augmentation. Albumentations supports all common computer vision tasks such as classification, semantic segmentation, instance segmentation, object detection, and pose estimation. \n<br>\n\n## Features\n\nPipelines based on hydra-core configs and PytorchLightning modules\n- Predefined folder structure. Modularity: all abstractions are split into different submodule\n- Rapid Experimentation. Thanks to automating pipeline with config files and hydra command line superpowers\n- Little Boilerplate. So pipeline can be easily modified\n- Main Configuration. Main config file specifies default training configuration\n- Experiment Configurations. Stored in a separate folder, they can be composed out of smaller configs, override chosen parameters or define everything from scratch\n- Experiment Tracking. Many logging frameworks can be easily integrated\n- Logs. All logs (checkpoints, data from loggers, chosen hparams, etc.) are stored in a convenient folder structure imposed by Hydra \n- Automates PyTorch Lightning training pipeline with little boilerplate, so it can be easily modified\n- Augmentations with [albumentations][albumentations-team/albumentations] described in a yaml config.\n- Support of [timm models][rwightman/pytorch-image-models], [pytorch-optimizer][jettify/pytorch-optimizer] and [TorchMetrics][PyTorchLightning/pytorch-metrics]\n- Exponential Moving Average for a more stable training, and Stochastic Moving Average for a better generalization and just overall performance.\n\n<br>\n\n## Project structure\nThe directory structure of new project looks like this: \n```\n├── src\n│   ├── fulmo\n│   │   ├── callbacks               <- PyTorch Lightning callbacks\n│   │   ├── core                    <- PyTorch Lightning models\n│   │   ├── datasets                <- PyTorch datasets\n│   │   ├── losses                  <- PyTorch losses\n│   │   ├── metrics                 <- PyTorch metrics  \n│   │   ├── models                  <- PyTorch model architectures\n│   │   ├── optimizers              <- PyTorch optimizers\n│   │   ├── readers                 <- Data readers\n│   │   ├── samples                 <- PyTorch samplers\n│   │   ├── schedulers              <- PyTorch schedulers\n│   │   └── utils\n├── tests\n│   ├── test_fulmo                  <- Tests\n│\n├── .bumpversion.cfg\n├── .darglint\n├── .gitignore\n├── .pre-commit-config.yaml <- Configuration of hooks for automatic code formatting\n├── CHANGELOG.md\n├── mypy.ini\n├── noxfile.py\n├── poetry.lock             <- File for installing python dependencies\n├── pyproject.toml          <- File for installing python dependencies\n├── README.md\n└── tasks.py\n```\n\n<br>\n\n## Workflow\n1. Write your PyTorch model\n2. Write your PyTorch Lightning datamodule\n3. Write your experiment config, containing paths to your model and datamodule\n4. Run training with chosen experiment config:<br>\n```bash\npython train.py +experiment=experiment_name\n```\n<br>\n\n## Experiment Tracking\nPyTorch Lightning provides built in loggers for Weights&Biases, Neptune, Comet, MLFlow, Tensorboard and CSV. To use one of them, simply add its config to [configs/logger](configs/logger) and run:\n ```yaml\npython train.py logger=logger_name\n```\n<br>\n\n## Quickstart\n\n<details>\n<summary>First, install dependencies</summary>\n\n```yaml\npip install fulmo | poetry add fulmo\n```\n\n</details>\n\n<details>\n<summary>Second, create your project</summary>\n\nSee [examples](https://github.com/jexio/g2net/tree/master/configs) folder.\n\n</details>\n\n<details>\n<summary>Next, you can train model with default configuration without logging</summary>\n\n```yaml\npython train.py\n```\n\n</details>\n\n<details>\n<summary>Or you can train model with chosen experiment config</summary>\n\n```yaml\npython train.py +experiment=experiment_name\n```\n\n</details>\n\n<details>\n<summary>Resume from a checkpoint</summary>\n\n```yaml\n# checkpoint can be either path or URL\n# path should be either absolute or prefixed with `${work_dir}/`\n# use quotes \'\' around argument or otherwise $ symbol breaks it\npython train.py \'+trainer.resume_from_checkpoint=${work_dir}/logs/runs/2021-06-23/16-50-49/checkpoints/last.ckpt\'\n```\n\n</details>\n\n<br>\n\n## TODO\n- [Data version control][dvc]\n- Metric learning pipeline\n- Integrate [Cross-Batch Memory for Embedding Learning (XBM)][msight-tech/research-xbm]\n- Image augmentation policies\n\n<br>\n\n## Credits\n* This package was created with [Cookiecutter][cookiecutter] and the [fedejaure/cookiecutter-modern-pypackage][cookiecutter-modern-pypackage] project template.\n* [hobogalaxy/lightning-hydra-template][hobogalaxy/lightning-hydra-template]\n* [Erlemar/pytorch_tempest][Erlemar/pytorch_tempest]\n* [bonlime/pytorch-tools][bonlime/pytorch-tools]\n\n\n[cookiecutter]: https://github.com/cookiecutter/cookiecutter\n[cookiecutter-modern-pypackage]: https://github.com/fedejaure/cookiecutter-modern-pypackage\n[PyTorchLightning/pytorch-lightning]: https://github.com/PyTorchLightning/pytorch-lightning\n[PyTorchLightning/pytorch-metrics]: https://github.com/PytorchLightning/metrics\n[hobogalaxy/lightning-hydra-template]: https://github.com/hobogalaxy/lightning-hydra-template\n[albumentations-team/albumentations]: https://github.com/albumentations-team/albumentations\n[facebookresearch/hydra]: https://github.com/facebookresearch/hydra\n[rwightman/pytorch-image-models]: https://github.com/rwightman/pytorch-image-models\n[jettify/pytorch-optimizer]: https://github.com/jettify/pytorch-optimizer\n[bonlime/pytorch-tools]: https://github.com/bonlime/pytorch-tools\n[Erlemar/pytorch_tempest]: https://github.com/Erlemar/pytorch_tempest\n[msight-tech/research-xbm]: https://github.com/msight-tech/research-xbm\n[mlflow]: https://mlflow.org/\n[dvc]: https://dvc.org/\n[ClearML]: https://clear.ml/\n[commitizen-tools/commitizen]: https://github.com/commitizen-tools/commitizen\n',
    'author': 'Gleb Glushkov',
    'author_email': 'ptjexio@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jexio/fulmo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
