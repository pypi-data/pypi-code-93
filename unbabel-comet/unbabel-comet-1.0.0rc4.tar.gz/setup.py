# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['comet',
 'comet.cli',
 'comet.encoders',
 'comet.models',
 'comet.models.ranking',
 'comet.models.regression',
 'comet.modules']

package_data = \
{'': ['*']}

install_requires = \
['jsonargparse==3.13.1',
 'pandas==1.1.5',
 'pytorch-lightning==1.3.5',
 'sentencepiece>=0.1.96,<0.2.0',
 'torch==1.6.0',
 'torchmetrics==0.5',
 'transformers>=4.8.2,<5.0.0']

entry_points = \
{'console_scripts': ['comet-compare = comet.cli.compare:compare_command',
                     'comet-score = comet.cli.score:score_command',
                     'comet-train = comet.cli.train:train_command']}

setup_kwargs = {
    'name': 'unbabel-comet',
    'version': '1.0.0rc4',
    'description': 'High-quality Machine Translation Evaluation',
    'long_description': '<p align="center">\n  <img src="https://raw.githubusercontent.com/Unbabel/COMET/master/docs/source/_static/img/COMET_lockup-dark.png">\n  <br />\n  <br />\n  <a href="https://github.com/Unbabel/COMET/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/github/license/Unbabel/COMET" /></a>\n  <a href="https://github.com/Unbabel/COMET/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/Unbabel/COMET" /></a>\n  <a href=""><img alt="PyPI" src="https://img.shields.io/pypi/v/unbabel-comet" /></a>\n  <a href="https://github.com/psf/black"><img alt="Code Style" src="https://img.shields.io/badge/code%20style-black-black" /></a>\n</p>\n\n## Quick Installation\n\nDetailed usage examples and instructions can be found in the [Full Documentation](https://unbabel.github.io/COMET/html/index.html).\n\nSimple installation from PyPI\n\nPre-release of version 1.0:\n```bash\npip install unbabel-comet==1.0.0rc4\n```\n\nTo develop locally install [Poetry](https://python-poetry.org/docs/#installation) and run the following commands:\n```bash\ngit clone https://github.com/Unbabel/COMET\npoetry install\n```\n\n## Scoring MT outputs:\n\n### Via Bash:\n\nExamples from WMT20:\n\n```bash\necho -e "Dem Feuer konnte Einhalt geboten werden\\nSchulen und Kindergärten wurden eröffnet." >> src.de\necho -e "The fire could be stopped\\nSchools and kindergartens were open" >> hyp.en\necho -e "They were able to control the fire.\\nSchools and kindergartens opened" >> ref.en\n```\n\n```bash\ncomet-score -s src.de -t hyp.en -r ref.en\n```\n\nYou can select another model/metric with the --model flag and for reference-free (QE-as-a-metric) models you don\'t need to pass a reference.\n\n```bash\ncomet-score -s src.de -t hyp.en --model wmt20-comet-qe-da\n```\n\nFollowing the work on [Uncertainty-Aware MT Evaluation]() you can use the --mc_dropout flag to get a variance/uncertainty value for each segment score. If this value is high, it means that the metric is less confident in that prediction.\n\n```bash\ncomet-score -s src.de -t hyp.en -r ref.en --mc_dropout 30\n```\n\nWhen comparing two MT systems we encourage you to run the `comet-compare` command to get a **contrastive statistical significance** with bootstrap resampling [(Koehn, et al 2004)](https://aclanthology.org/W04-3250/).\n\n```bash\ncomet-compare --help\n```\n\nFor even more detailed MT contrastive evaluation please take a look at our new tool [MT-Telescope](https://github.com/Unbabel/MT-Telescope).\n\n### Scoring within Python:\n\n```python\nfrom comet import download_model, load_from_checkpoint\n\nmodel_path = download_model("wmt20-comet-da")\nmodel = load_from_checkpoint(model_path)\ndata = [\n    {\n        "src": "Dem Feuer konnte Einhalt geboten werden",\n        "mt": "The fire could be stopped",\n        "ref": "They were able to control the fire."\n    },\n    {\n        "src": "Schulen und Kindergärten wurden eröffnet.",\n        "mt": "Schools and kindergartens were open",\n        "ref": "Schools and kindergartens opened"\n    }\n]\nseg_scores, sys_score = model.predict(data, batch_size=8, gpus=1)\n```\n\n### Languages Covered:\n\nAll the above mentioned models are build on top of XLM-R which cover the following languages:\n\nAfrikaans, Albanian, Amharic, Arabic, Armenian, Assamese, Azerbaijani, Basque, Belarusian, Bengali, Bengali Romanized, Bosnian, Breton, Bulgarian, Burmese, Burmese, Catalan, Chinese (Simplified), Chinese (Traditional), Croatian, Czech, Danish, Dutch, English, Esperanto, Estonian, Filipino, Finnish, French, Galician, Georgian, German, Greek, Gujarati, Hausa, Hebrew, Hindi, Hindi Romanized, Hungarian, Icelandic, Indonesian, Irish, Italian, Japanese, Javanese, Kannada, Kazakh, Khmer, Korean, Kurdish (Kurmanji), Kyrgyz, Lao, Latin, Latvian, Lithuanian, Macedonian, Malagasy, Malay, Malayalam, Marathi, Mongolian, Nepali, Norwegian, Oriya, Oromo, Pashto, Persian, Polish, Portuguese, Punjabi, Romanian, Russian, Sanskri, Scottish, Gaelic, Serbian, Sindhi, Sinhala, Slovak, Slovenian, Somali, Spanish, Sundanese, Swahili, Swedish, Tamil, Tamil Romanized, Telugu, Telugu Romanized, Thai, Turkish, Ukrainian, Urdu, Urdu Romanized, Uyghur, Uzbek, Vietnamese, Welsh, Western, Frisian, Xhosa, Yiddish.\n\n**Thus, results for language pairs containing uncovered languages are unreliable!**\n\n## COMET Models:\n\nWe recommend the two following models to evaluate your translations:\n\n- `wmt20-comet-da`: **DEFAULT** Reference-based Regression model build on top of XLM-R (large) and trained of Direct Assessments from WMT17 to WMT19. Same as `wmt-large-da-estimator-1719` from previous versions.\n- `wmt20-comet-qe-da`: **Reference-FREE** Regression model build on top of XLM-R (large) and trained of Direct Assessments from WMT17 to WMT19. Same as `wmt-large-qe-estimator-1719` from previous versions.\n\nThis two models were developed to participate on the WMT20 Metrics shared task [(Mathur et al. 2020)](https://aclanthology.org/2020.wmt-1.77.pdf). This two metric/models are to the date, the best performing metrics at segment-level in the MQM data released recently by Google [(Freitag et al. 2020)](https://arxiv.org/pdf/2104.14478.pdf). Also, in a large-scale study performed by Microsoft Research this two metrics ranked 1st and 2nd in terms of system-level decision accuracy [(Kocmi et al. 2020)](https://arxiv.org/pdf/2107.10821.pdf).\n\nFor more information about the available COMET models we invite you to read our metrics descriptions [here](METRICS.md)\n\n## Train your own Metric: \n\nInstead of using pretrained models your can train your own model with the following command:\n```bash\ncomet-train --cfg configs/models/{your_model_config}.yaml\n```\n\n## unittest:\nIn order to run the toolkit tests you must run the following command:\n\n```bash\ncoverage run --source=comet -m unittest discover\ncoverage report -m\n```\n\n## Publications\n\n- [COMET: A Neural Framework for MT Evaluation](https://www.aclweb.org/anthology/2020.emnlp-main.213)\n\n- [Unbabel\'s Participation in the WMT20 Metrics Shared Task](https://aclanthology.org/2020.wmt-1.101/)\n\n- [COMET - Deploying a New State-of-the-art MT Evaluation Metric in Production](https://www.aclweb.org/anthology/2020.amta-user.4)\n',
    'author': 'Ricardo Rei, Craig Stewart, Catarina Farinha, Alon Lavie',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Unbabel/COMET',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
