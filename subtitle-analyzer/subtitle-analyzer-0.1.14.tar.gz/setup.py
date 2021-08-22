# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['subtitle_analyzer']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'pysubs2>=1.1.0,<2.0.0',
 'sencore>=0.1.28,<0.2.0',
 'subtitlecore>=0.1.11,<0.2.0',
 'x2cdict>=0.1.42,<0.2.0']

entry_points = \
{'console_scripts': ['sta_phrase = subtitle_analyzer.entry:subtitle_phrase',
                     'sta_reviewed_phrase = subtitle_analyzer.tbr: '
                     'gen_phrase_ass',
                     'sta_vocab = subtitle_analyzer.entry:subtitle_vocab',
                     'tbr_phrase = subtitle_analyzer.tbr:subtitle_phrase']}

setup_kwargs = {
    'name': 'subtitle-analyzer',
    'version': '0.1.14',
    'description': '',
    'long_description': '# Installation from pip3\n\n```shell\npip3 install --verbose subtitle_analyzer\npython -m spacy download en_core_web_trf\npython -m spacy download es_dep_news_trf\n```\n\n# Usage\n\nPlease refer to [api docs](https://qishe-nlp.github.io/subtitle-analyzer/).\n\n### Excutable usage\n\n* Write ass file with vocabulary information\n\n```shell\nsta_vocab --srtfile movie.srt --lang en --assfile en_vocab.ass --google False\n``` \n\n* Write ass file with phrase information \n\n```shell\nsta_phrase --srtfile movie.srt --lang en --assfile en_phrase.ass --google False\n```\n\n### Package usage\n```\nfrom subtitlecore import Subtitle\nfrom subtitle_analyzer import VocabAnalyzer, PhraseAnalyzer\nfrom subtitle_analyzer import VocabASSWriter, PhraseASSWriter\nimport json\n\ndef subtitle_vocab(srtfile, lang, assfile, google):\n\n  phase = {"step": 1, "msg": "Start sentenizing"}\n  print(json.dumps(phase), flush=True)\n\n  sf = Subtitle(srtfile, lang)\n  sens = sf.sentenize()\n  for e in sens:\n    print(e)\n\n  phase = {"step": 2, "msg": "Finish sentenizing"}\n  print(json.dumps(phase), flush=True)\n\n  analyzer = VocabAnalyzer(lang)\n  exs = analyzer.get_line_vocabs(sens, google)\n  shown = exs[:20]\n\n  phase = {"step": 3, "msg": "Finish vocabs dictionary lookup", "vocabs": shown}\n  print(json.dumps(phase), flush=True)\n\n  if assfile:\n    ass_writer = VocabASSWriter(srtfile)\n    ass_writer.write(exs, assfile, {"animation": False})\n    \n    phase = {"step": 4, "msg": "Finish ass saving"} \n    print(json.dumps(phase), flush=True)\n\ndef subtitle_phrase(srtfile, lang, assfile, google):\n\n  phase = {"step": 1, "msg": "Start sentenizing"}\n  print(json.dumps(phase), flush=True)\n\n  sf = Subtitle(srtfile, lang)\n  sens = sf.sentenize()\n  for e in sens:\n    print(e)\n\n  phase = {"step": 2, "msg": "Finish sentenizing"}\n  print(json.dumps(phase), flush=True)\n\n  analyzer = PhraseAnalyzer(lang)\n  exs = analyzer.get_line_phrases(sens, google)\n\n  phase = {"step": 3, "msg": "Finish phrases dictionary lookup", "vocabs": exs[:10]}\n  print(json.dumps(phase), flush=True)\n\n  if assfile:\n    ass_writer = PhraseASSWriter(srtfile)\n    ass_writer.write(exs, assfile, {"animation": False})\n    \n    phase = {"step": 4, "msg": "Finish ass saving"} \n    print(json.dumps(phase), flush=True)\n```\n\n# Development\n\n### Clone project\n```\ngit clone https://github.com/qishe-nlp/subtitle-analyzer.git\n```\n\n### Install [poetry](https://python-poetry.org/docs/)\n\n### Install dependencies\n```\npoetry update\n```\n\n### Test\n```\npoetry run pytest -rP\n```\nwhich run tests under `tests/*`\n\n### Execute\n```\npoetry run sta_vocab --help\npoetry run sta_phrase --help\n```\n\n### Create sphinx docs\n```\npoetry shell\ncd apidocs\nsphinx-apidoc -f -o source ../subtitle_analyzer\nmake html\npython -m http.server -d build/html\n```\n\n### Hose docs on github pages\n```\ncp -rf apidocs/build/html/* docs/\n```\n\n### Build\n* Change `version` in `pyproject.toml` and `subtitle_analyzer/__init__.py`\n* Build python package by `poetry build`\n\n### Git commit and push\n\n### Publish from local dev env\n* Set pypi test environment variables in poetry, refer to [poetry doc](https://python-poetry.org/docs/repositories/)\n* Publish to pypi test by `poetry publish -r test`\n\n### Publish through CI \n\n* Github action build and publish package to [test pypi repo](https://test.pypi.org/)\n\n```\ngit tag [x.x.x]\ngit push origin master\n```\n\n* Manually publish to [pypi repo](https://pypi.org/) through [github action](https://github.com/qishe-nlp/subtitle-analyzer/actions/workflows/pypi.yml)\n\n',
    'author': 'Phoenix Grey',
    'author_email': 'phoenix.grey0108@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/qishe-nlp/subtitle-analyzer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
