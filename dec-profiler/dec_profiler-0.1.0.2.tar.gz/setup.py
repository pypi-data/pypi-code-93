# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dec_profiler', 'dec_profiler.test']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'dec-profiler',
    'version': '0.1.0.2',
    'description': 'Тестирование производительности кода',
    'long_description': '# Что это ?\nПроект для профилирования кода\n\n\n# Описание модулей\n\n\n## time_dec - Замерить Время\n\nПример работы\n```python\nimport random\nfrom time_dec import time_s\n\n\n@time_s(3)\ndef test():\n    a = []\n    for i in range(7000):\n        a.append(random.randint(0, 9))\n\nn = 100\na = []\ntest()\n```\n\n\n+ `time_s(count_loop)` = Замерить время выполнения в секундах\n    + `count_loop` = Количество повторений функции\n\n\n+ `time_ns(count_loop)` = Замерить время выполнения в наносекундах\n    + `count_loop` = Количество повторений функции',
    'author': 'Denis Kustov',
    'author_email': 'denis-kustov@rambler.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/denisxab/dec_profiler',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
