# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['minichat']

package_data = \
{'': ['*'], 'minichat': ['aiml_data/alice/*', 'aiml_data/custom/*']}

install_requires = \
['python-aiml==0.9.3']

setup_kwargs = {
    'name': 'minichat',
    'version': '1.0.3',
    'description': 'Mini chatbot client based on AIML',
    'long_description': '# Minichat\nMini chatbot client based on AIML\n\n# Installation\n\n```sh\npip3 install minichat\n```\n\n# Example\n\n```py\nfrom minichat import minichat\n\nchatbot = minichat.Minichat()\n\nwhile True:\n    question = input("You: ")\n    answer = chatbot.chat(question)\n    print("Bot:", answer)\n```\n\n## Created and maintained by SnowflakeDev Community ❄️',
    'author': 'DevAndromeda',
    'author_email': 'devandromeda@snowflakedev.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DevSnowflake/minichat',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
