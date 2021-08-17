# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['super_image',
 'super_image.data',
 'super_image.models',
 'super_image.models.a2n',
 'super_image.models.carn',
 'super_image.models.drln',
 'super_image.models.edsr',
 'super_image.models.jiif',
 'super_image.models.liif',
 'super_image.models.masa',
 'super_image.models.mdsr',
 'super_image.models.msrn',
 'super_image.models.pan',
 'super_image.models.rcan',
 'super_image.models.smsr',
 'super_image.utils']

package_data = \
{'': ['*']}

install_requires = \
['h5py==3.1.0',
 'huggingface-hub>=0.0.13,<0.0.14',
 'opencv-python==4.5.2.54',
 'torch==1.9.0',
 'torchvision==0.10.0',
 'tqdm==4.61.2']

entry_points = \
{'console_scripts': ['super-image = super_image.cli:main']}

setup_kwargs = {
    'name': 'super-image',
    'version': '0.1.4',
    'description': 'State-of-the-art image super resolution models for PyTorch.',
    'long_description': '<h1 align="center">super-image</h1>\n\n<p align="center">\n    <a href="https://eugenesiow.github.io/super-image/">\n        <img alt="documentation" src="https://img.shields.io/badge/docs-mkdocs-blue.svg?style=flat">\n    </a>\n    <a href="https://github.com/eugenesiow/super-image/blob/main/LICENSE">\n\t\t<img alt="GitHub" src="https://img.shields.io/github/license/eugenesiow/super-image.svg?color=blue">\n\t</a>\n    <a href="https://pypi.org/project/super-image/">\n        <img alt="pypi version" src="https://img.shields.io/pypi/v/super-image.svg">\n    </a>\n</p>\n\n<h3 align="center">\n    <p>State-of-the-art image super resolution models for PyTorch.</p>\n</h3>\n\n## Installation\n\nWith `pip`:\n```bash\npip install super-image\n```\n\n## Quick Start\n\nQuickly utilise pre-trained models for upscaling your images 2x, 3x and 4x. See the full list of models [below](#pre-trained-models).\n\n[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eugenesiow/super-image-notebooks/blob/master/notebooks/Upscale_Images_with_Pretrained_super_image_Models.ipynb "Open in Colab")\n\n```python\nfrom super_image import EdsrModel, ImageLoader\nfrom PIL import Image\nimport requests\n\nurl = \'https://paperswithcode.com/media/datasets/Set5-0000002728-07a9793f_zA3bDjj.jpg\'\nimage = Image.open(requests.get(url, stream=True).raw)\n\nmodel = EdsrModel.from_pretrained(\'eugenesiow/edsr-base\', scale=2)\ninputs = ImageLoader.load_image(image)\npreds = model(inputs)\n\nImageLoader.save_image(preds, \'./scaled_2x.png\')\nImageLoader.save_compare(inputs, preds, \'./scaled_2x_compare.png\')\n```\n\n## Pre-trained Models\nPre-trained models are available at various scales and hosted at the awesome [`huggingface_hub`](https://huggingface.co/models?filter=super-image). By default the models were pretrained on [DIV2K](https://huggingface.co/datasets/eugenesiow/Div2k), a dataset of 800 high-quality (2K resolution) images for training, augmented to 4000 images and uses a dev set of 100 validation images (images numbered 801 to 900). \n\nThe leaderboard below shows the \n[PSNR](https://en.wikipedia.org/wiki/Peak_signal-to-noise_ratio#Quality_estimation_with_PSNR) / [SSIM](https://en.wikipedia.org/wiki/Structural_similarity#Algorithm) \nmetrics for each model at various scales on various test sets ([Set5](https://huggingface.co/datasets/eugenesiow/Set5), \n[Set14](https://huggingface.co/datasets/eugenesiow/Set14), \n[BSD100](https://huggingface.co/datasets/eugenesiow/BSD100), \n[Urban100](https://huggingface.co/datasets/eugenesiow/Urban100)). The **higher the better**. \nAll training was to 1000 epochs (some publications, like a2n, train to >1000 epochs in their experiments). \n\n### Scale x2\n\n|Rank   |Model  \t                                                |Params         |Set5  \t            |Set14  \t        |BSD100  \t        |Urban100  \t        |\n|---    |---\t                                                    |---            |---                |---\t            |---\t            |---\t            |\n|1      |[msrn](https://huggingface.co/eugenesiow/msrn)  \t        |5.9m           |**38.08/0.9609**   |**33.75/0.9183**  \t|**33.82/0.9258**   |**32.14/0.9287**   |\n|2      |[msrn-bam](https://huggingface.co/eugenesiow/msrn-bam)  \t|5.9m           |38.02/0.9608       |33.73/0.9186  \t    |**33.78/0.9253**   |32.08/0.9276       |\n|2      |[edsr-base](https://huggingface.co/eugenesiow/edsr-base)  \t|1.5m           |38.02/0.9607       |33.66/0.9180       |33.77/0.9254       |32.04/0.9276       |\n|3      |[a2n](https://huggingface.co/eugenesiow/a2n)   \t        |1.0m           |37.87/0.9602       |33.54/0.9171       |33.67/0.9244       |31.71/0.9240       |\n|4      |[carn-bam](https://huggingface.co/eugenesiow/carn-bam)     |1.6m           |37.83/0.96         |33.51/0.9166       |33.64/0.924        |31.53/0.922        |\n|5      |[pan-bam](https://huggingface.co/eugenesiow/pan-bam)       |260k           |37.7/0.9596        |33.4/0.9161        |33.6/0.9234        |31.35/0.92         |\n\n### Scale x3\n\n|Rank   |Model  \t                                                |Params         |Set5  \t            |Set14  \t        |BSD100  \t        |Urban100  \t        |\n|---    |---\t                                                    |---            |---                |---\t            |---\t            |---\t            |\n|1      |[msrn](https://huggingface.co/eugenesiow/msrn)             |6.1m           |35.12/0.9409       |**31.08/0.8593**   |**29.67/0.8198**   |**29.31/0.8743**   |\n|2      |[msrn-bam](https://huggingface.co/eugenesiow/msrn-bam)  \t|5.9m           |**35.13/0.9408**   |31.06/0.8588  \t    |29.65/0.8196       |29.26/0.8736       |\n|3      |[edsr-base](https://huggingface.co/eugenesiow/edsr-base)  \t|1.5m           |35.01/0.9402       |31.01/0.8583       |29.63/0.8190       |29.19/0.8722       |\n|4      |[a2n](https://huggingface.co/eugenesiow/a2n)   \t        |1.0m           |34.8/0.9387        |30.94/0.8568       |29.56/0.8173       |28.95/0.8671       |\n|5      |[carn-bam](https://huggingface.co/eugenesiow/carn-bam)     |1.6m           |34.82/0.9385       |30.9/0.8558        |29.54/0.8166       |28.84/0.8648       |\n|6      |[pan-bam](https://huggingface.co/eugenesiow/pan-bam)       |260k           |34.62/0.9371       |30.83/0.8545       |29.47/0.8153       |28.64/0.861        |\n\n### Scale x4\n\n|Rank   |Model  \t                                                |Params         |Set5  \t            |Set14  \t        |BSD100  \t        |Urban100  \t        |\n|---    |---\t                                                    |---            |---                |---\t            |---\t            |---\t            |\n|1      |[msrn](https://huggingface.co/eugenesiow/msrn)             |6.1m           |32.19/0.8951       |**28.78/0.7862**   |**28.53/0.7657**   |**26.12/0.7866**   |\n|2      |[msrn-bam](https://huggingface.co/eugenesiow/msrn-bam)  \t|5.9m           |**32.26/0.8955**   |28.78/0.7859       |28.51/0.7651       |26.10/0.7857       |\n|3      |[edsr-base](https://huggingface.co/eugenesiow/edsr-base)  \t|1.5m           |32.12/0.8947       |28.72/0.7845       |28.50/0.7644       |26.02/0.7832       |\n|4      |[a2n](https://huggingface.co/eugenesiow/a2n)               |1.0m           |32.07/0.8933       |28.68/0.7830       |28.44/0.7624       |25.89/0.7787       |\n|5      |[carn](https://huggingface.co/eugenesiow/carn)             |1.6m           |32.05/0.8931       |28.67/0.7828       |28.44/0.7625       |25.85/0.7768       |\n|6      |[carn-bam](https://huggingface.co/eugenesiow/carn-bam)     |1.6m           |32.0/0.8923        |28.62/0.7822       |28.41/0.7614       |25.77/0.7741       |\n|7      |[pan-bam](https://huggingface.co/eugenesiow/pan-bam)       |270k           |31.9/0.8911        |28.54/0.7795       |28.32/0.7591       |25.6/0.7691        |\n\nYou can find a notebook to easily run evaluation on pretrained models below:\n\n[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eugenesiow/super-image-notebooks/blob/master/notebooks/Evaluate_Pretrained_super_image_Models.ipynb "Open in Colab")\n\n## Train Models\n\nWe need the huggingface [datasets](https://huggingface.co/datasets?filter=task_ids:other-other-image-super-resolution) library to download the data:\n```bash\npip install datasets\n```\nThe following code gets the data and preprocesses/augments the data.\n\n```python\nfrom datasets import load_dataset\nfrom super_image.data import EvalDataset, TrainDataset, augment_five_crop\n\naugmented_dataset = load_dataset(\'eugenesiow/Div2k\', \'bicubic_x4\', split=\'train\')\\\n    .map(augment_five_crop, batched=True, desc="Augmenting Dataset")                                # download and augment the data with the five_crop method\ntrain_dataset = TrainDataset(augmented_dataset)                                                     # prepare the train dataset for loading PyTorch DataLoader\neval_dataset = EvalDataset(load_dataset(\'eugenesiow/Div2k\', \'bicubic_x4\', split=\'validation\'))      # prepare the eval dataset for the PyTorch DataLoader\n```\n\nThe training code is provided below:\n```python\nfrom super_image import Trainer, TrainingArguments, EdsrModel, EdsrConfig\n\ntraining_args = TrainingArguments(\n    output_dir=\'./results\',                 # output directory\n    num_train_epochs=1000,                  # total number of training epochs\n)\n\nconfig = EdsrConfig(\n    scale=4,                                # train a model to upscale 4x\n)\nmodel = EdsrModel(config)\n\ntrainer = Trainer(\n    model=model,                         # the instantiated model to be trained\n    args=training_args,                  # training arguments, defined above\n    train_dataset=train_dataset,         # training dataset\n    eval_dataset=eval_dataset            # evaluation dataset\n)\n\ntrainer.train()\n```\n\n[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eugenesiow/super-image-notebooks/blob/master/notebooks/Train_super_image_Models.ipynb "Open in Colab")',
    'author': 'Eugene Siow',
    'author_email': 'kyo116@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/eugenesiow/super-image',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
