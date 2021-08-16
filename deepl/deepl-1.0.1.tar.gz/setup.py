# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deepl']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.18,<3.0']

entry_points = \
{'console_scripts': ['deepl = deepl.__main__:main']}

setup_kwargs = {
    'name': 'deepl',
    'version': '1.0.1',
    'description': 'Python library for the DeepL API.',
    'long_description': '# DeepL Python Library\n\n[![PyPI version](https://img.shields.io/pypi/v/deepl.svg)](https://pypi.org/project/deepl/)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/deepl.svg)](https://pypi.org/project/deepl/)\n[![License: MIT](https://img.shields.io/badge/license-MIT-blueviolet.svg)](https://github.com/DeepLcom/deepl-python/blob/main/LICENSE)\n\nThe [DeepL API](https://www.deepl.com/docs-api?utm_source=github&utm_medium=github-python-readme) is a language\ntranslation API that allows other computer programs to send texts and documents to DeepL\'s servers and receive\nhigh-quality translations. This opens a whole universe of opportunities for developers: any translation product you can\nimagine can now be built on top of DeepL\'s best-in-class translation technology.\n\nThe DeepL Python library offers a convenient way for applications written in Python to interact with the DeepL API. We\nintend to support all API functions with the library, though support for new features may be added to the library after\nthey’re added to the API.\n\n\n## Getting an authentication key \n\nTo use the DeepL Python Library, you\'ll need an API authentication key. To get a key, [please create an account here](https://www.deepl.com/pro?utm_source=github&utm_medium=github-python-readme#developer). You can translate up to 500,000 characters/month for free. \n\n## Installation\nThe library can be installed from [PyPI](https://pypi.org/project/deepl/) using pip:\n```shell\npip install --upgrade deepl\n```\n\nIf you need to modify this source code, install the dependencies using poetry:\n```shell\npoetry install\n```\n\n### Requirements\nThe library is tested with Python versions 3.6 to 3.9. \n\nThe `requests` module is used to perform HTTP requests; the minimum is version 2.18.\n\n## Usage\n\n```python\nimport deepl\n\n# Create a Translator object providing your DeepL API authentication key\ntranslator = deepl.Translator("YOUR_AUTH_KEY")\n\n# Translate text into a target language, in this case, French\nresult = translator.translate_text("Hello, world!", target_lang="FR")\nprint(result)  # "Bonjour, le monde !"\n# Note: printing or converting the result to a string uses the output text\n\n# Translate multiple texts into British English\nresult = translator.translate_text(["お元気ですか？", "¿Cómo estás?"], target_lang="EN-GB")\nprint(result[0].text)  # "How are you?"\nprint(result[0].detected_source_lang)  # "JA"\nprint(result[1].text)  # "How are you?"\nprint(result[1].detected_source_lang)  # "ES"\n\n# Translating documents\ntranslator.translate_document_from_filepath(\n    "Instruction Manual.docx",\n    "Bedienungsanleitlung.docx",\n    target_lang="DE",\n    formality="more"\n)\n\n# Check account usage\nusage = translator.get_usage()\nif usage.character.limit_exceeded:\n    print("Character limit exceeded.")\n\n# Source and target languages\nfor language in translator.get_source_languages():\n    print(f"{language.code} ({language.name})")  # Example: "DE (German)"\n\nnum_languages = sum([language.supports_formality\n                     for language in translator.get_target_languages()])\nprint(f"{num_languages} target languages support formality parameter")\n```\n### Logging\nLogging can be enabled to see the HTTP-requests sent and responses received by the library. Enable and control logging\nusing Python\'s logging module, for example:\n```python\nimport logging\nlogging.basicConfig()\nlogging.getLogger(\'deepl\').setLevel(logging.DEBUG)\n```\n\n### Exceptions\nAll module functions may raise `deepl.DeepLException` or one of its subclasses.\nIf invalid arguments are provided, they may raise the standard exceptions `ValueError` and `TypeError`. \n\n## Command Line Interface\nThe library can be run on the command line supporting all API functions. Use the `--help` option for \nusage information:\n```shell\npython3 -m deepl --help\n```\nThe CLI requires your DeepL authentication key specified either as the `DEEPL_AUTH_KEY` environment variable, or using\nthe `--auth-key` option, for example:\n```shell\npython3 -m deepl --auth-key=YOUR_AUTH_KEY usage\n```\nNote that the `--auth-key` argument must appear *before* the command argument. The recognized commands are:\n\n| Command   | Description                                            |\n| :-------- | :----------------------------------------------------- |\n| text      | translate text(s)                                      |\n| document  | translate document(s)                                  |\n| usage     | print usage information for the current billing period |\n| languages | print available languages                              |\n\nFor example, to translate text:\n```shell\npython3 -m deepl --auth-key=YOUR_AUTH_KEY text --to=DE "Text to be translated."\n```\nWrap text arguments in quotes to prevent the shell from splitting sentences into words.\n\n## Development\nThe test suite depends on [deepl-mock](https://www.github.com/DeepLcom/deepl-mock). Run it in another terminal while executing the tests, using port 3000. Set the mock-server listening port using the environment variable `DEEPL_MOCK_SERVER_PORT`. \n\nExecute the tests using `tox`.\n\n### Issues\nIf you experience problems using the library, or would like to request a new feature, please create an\n[issue](https://www.github.com/DeepLcom/deepl-python/issues). \n',
    'author': 'DeepL GmbH',
    'author_email': 'python-api@deepl.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeepLcom/deepl-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4',
}


setup(**setup_kwargs)
