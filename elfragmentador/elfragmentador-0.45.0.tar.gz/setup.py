# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['elfragmentador']

package_data = \
{'': ['*'], 'elfragmentador': ['htmlcov/*']}

install_requires = \
['future-annotations>=1.0.0,<2.0.0',
 'llvmlite>=0.36.0,<0.37.0',
 'lxml>=4.6.3,<5.0.0',
 'networkx>=2.5,<3.0',
 'numpy>=1.19.0,<2.0.0',
 'pandas>=1.0.0,<2.0.0',
 'pyteomics>=4.4.2,<5.0.0',
 'pytorch-lightning>=1.2.0,<2.0.0',
 'torch>=1.7.0,<2.0.0',
 'uniplot>=0.3.5,<0.4.0',
 'wandb>=0.10.13,<0.11.0']

extras_require = \
{':python_version < "3.7"': ['fsspec>=0.8.5,<0.9.0'],
 ':python_version < "3.8"': ['importlib-metadata>=1.0,<2.0']}

entry_points = \
{'console_scripts': ['elfragmentador_append_pin = '
                     'elfragmentador.cli:append_predictions',
                     'elfragmentador_calculate_irt = '
                     'elfragmentador.cli:calculate_irt',
                     'elfragmentador_convert_sptxt = '
                     'elfragmentador.cli:convert_sptxt',
                     'elfragmentador_evaluate = '
                     'elfragmentador.cli:evaluate_checkpoint',
                     'elfragmentador_predict_csv = '
                     'elfragmentador.cli:predict_csv',
                     'elfragmentador_train = elfragmentador.cli:train']}

setup_kwargs = {
    'name': 'elfragmentador',
    'version': '0.45.0',
    'description': 'Predicts peptide fragmentations using transformers',
    'long_description': '# ElFragmentador\n\n## ElFragmentador\n\nThis repository attempts to implement a neural net that leverages the transformer architecture to predict peptide\nproperties (retention time and fragmentation).\n\n![](img/schematic.png)\n\n## Installation\n\nSince the project is currently in development mode, the best way to install is using pip from the cloned repo\n\n```shell\ngit clone https://github.com/jspaezp/elfragmentador.git\ncd elfragmentador\n\npip install /content/elfragmentador\n```\n\nNontheless, there is also a pipy installable version\n\n```shell\npip install elfragmentador\n```\n\n## Usage\n\n### Training\n\n```shell\n# Be a good person and keep track of your experiments, use wandb\n$ wandb login\n```\n\n```shell\nelfragmentador_train \\\n     --run_name onecycle_5e_petite_ndl4 \\\n     --scheduler onecycle \\\n     --max_epochs 5 \\\n     --lr_ratio 25 \\\n     --terminator_patience 20 \\\n     --lr 0.00005 \\\n     --gradient_clip_val 1.0 \\\n     --dropout 0.1 \\\n     --nhead 4 \\\n     --nhid 512 \\\n     --ninp 224 \\\n     --num_decoder_layers 4 \\\n     --num_encoder_layers 2 \\\n     --batch_size 400 \\\n     --accumulate_grad_batches 1 \\\n     --precision 16 \\\n     --gpus 1 \\\n     --progress_bar_refresh_rate 5 \\\n     --data_dir  /content/20210217-traindata\n```\n\n### Prediction\n\n#### Check performance\n\nI have implemented a way to compare the predictions of\nthe model with an `.sptxt` file. I generate them by using\n`comet > mokapot > spectrast` but alternatives can be used. \n\n```shell\nelfragmentador_evaluate --sptxt {my_sptxt_file} {path_to_my_checkpoint}\n```\n\n#### Predict Spectra\n\nYou can use it from python like so ...\n\n```python\ncheckpoint_path = "some/path/to/a/checkpoint"\nmodel = PepTransformerModel.load_from_checkpoint(checkpoint_path)\n\n# Set the model as evaluation mode\n_ = model.eval()\nmodel.predict_from_seq("MYPEPTIDEK", charge=2, nce=27.0)\n```\n\nIf you want to use graphical interface, I am currently working in\na flask app to visualize the results.\n\nIt can be run using flask.\n\n```shell\ngit clone https://github.com/jspaezp/elfragmentador.git\ncd elfragmentador/viz_app\n\n# Here you can install the dependencies using poetry\npython main.py\n```\n\n## Why transformers?\n\nBecause we can... Just kidding\n\nThe transformer architecture provides several benefits over the standard approach on fragment prediction (LSTM/RNN). On the training side it allows the parallel computation of whole sequences, whilst in LSTMs one element has to be passed at a time. In addition it gives the model itself a better chance to study the direct interactions between the elements that are being passed.\n\nOn the other hand, it allows a much better interpretability of the model, since the \'self-attention\' can be visualized on the input and in that way see what the model is focusing on while generating the prediction.\n\n## Inspiration for this project\n\nMany of the elements from this project are actually a combination of the principles shown in the [*Prosit* paper](https://www.nature.com/articles/s41592-019-0426-7) and the [Skyline poster](https://skyline.ms/_webdav/home/software/Skyline/%40files/2019-ASBMB-Rohde.pdf) on some of the elements to encode the peptides and the output fragment ions.\n\nOn the transformer side of things I must admit that many of the elements of this project are derived from [DETR:  End to end detection using transformers](https://github.com/facebookresearch/detr) in particular the trainable embeddings as an input for the decoder and some of the concepts discussed about it on [Yannic Kilcher\'s Youtube channel](https://youtu.be/T35ba_VXkMY) (which I highly recommend).\n\n## Why the name?\n\nTwo main reasons ... it translates to \'The fragmenter\' in spanish and the project intends to predic framgnetations. On the other hand ... The name was free in pypi.\n\n## Resources on transformers\n\n- An amazing illustrated guide to understand the transformer architecture: <http://jalammar.github.io/illustrated-transformer/>\n- Full implementation of a transformer in pytorch with the explanation of each part: <https://nlp.seas.harvard.edu/2018/04/03/attention.html>\n- Official pytorch implementation of the transformer: <https://pytorch.org/docs/stable/generated/torch.nn.Transformer.html>\n\n## How fast is it?\n\nYou can check how fast the model is in you specific system.\nRight now it tests only on CPU, message me if you need GPU inference times\n\n```shell\npoetry run pytest tests/test_model.py --benchmark-histogram \n```\n\nCurrenty the inference time in an Intel i5-7260U is ~5.9ms, or ~167.44 predictions per second. On a GPU it is closer to ~1000 predictions per second.\n\n## How big is it?\n\nI have explored many variations on the model but currently the one distributed is only ~4mb. Models up to 200mb have been tried and they don\'t really give a big improvement in performance.\n## "Common" questions\n\n- What scale are the retention times predicted.\n  - Out of the model it uses a scaled version of the Biognosys retention time\n    scale, so if using the base model, you will need to multiply by 100 and then\n    you will get something compatible with the iRT kit.\n- Is it any good?\n  - Well ... yes but if you want to see if it is good for you own data I have\n    added an API to test the model on a spectral library (made with spectrast).\n    Just get a checkpoint of the model,\n    run the command: `elfragmentador_evaluate {your_checkpoint.ckpt} {your_splib.sptxt}`\n  - TODO add some benchmarking metrics to this readme ...\n- Crosslinked peptides?\n  - No\n- ETD ?\n  - No\n- CID ?\n  - No\n- Glycosilation ?\n  - No\n- Negative Mode ?\n  - No\n- No ?\n  - Not really ... I think all of those are interesting questions but\n    AS IT IS RIGHT NOW it is not within the scope of the project. If you want\n    to discuss it, write an issue in the repo and we can see if it is feasible.\n\n### Known Issues\n\n- When setting `--max_spec` on `elfragmentador_evaluate --sptxt`, the retention time accuracy is not calculated correctly because the retention times are scaled within the selected range. Since the spectra are subset in their import order, therefore only the first-eluting peptides are used.\n\n### TODO list\n\n#### Urgent\n\n- Decouple to a different package with less dependencies\n  the inference side of things\n- Make a better logging output for the training script\n- Complete dosctrings and add documentation website\n- Allow training with missing values (done for RT, not for spectra)\n- Migrate training data preparation script to snakemake\n  - In Progress\n\n#### Possible\n\n- Add neutral losses specific to some PTMs\n- consider if using pyteomics as  a backend for most ms-related tasks\n- Translate annotation functions (getting ions) to numpy/torch\n- Add weights during training so psms that are more likel to be false positives weight less\n\n#### If I get time\n\n- Write ablation models and benchmark them (remove parts of the model and see how much worse it gets without it)\n\n## Acknowledgements\n\n1. Purdue Univ for the computational resources for the preparation of the data (Brown Cluster).\n2. Pytorch Lightning Team ... without this being open sourced this would not be posible.\n3. Weights and Biases (same as above).\n',
    'author': 'J. Sebastian Paez',
    'author_email': 'jspaezp@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
