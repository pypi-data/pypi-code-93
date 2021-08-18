# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['date_assistant']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'date-assistant',
    'version': '0.5.3',
    'description': '',
    'long_description': "# Date Assistant\n\n## Usage\n\n### Get the difference of days, months or years between 2 dates\n```py\nfrom date_assistant import DateAssistant\n\nmy_birthday_2021 = DateAssistant('2021-07-13')\ndate_assistant_birthday = '2021-08-18'\n\nmy_birthday_2021.days_diff_with(date_assistant_birthday)\n# 36\nmy_birthday_2021.months_diff_with(date_assistant_birthday)\n# 1\n\n```\n\n### Get the amount of years or months started since or until some date\n```py\nfrom date_assistant import DateAssistant\n\ndate_assistant_birthday = '2021-08-18'\nlast_day_of_2021 = DateAssistant('2021-12-31')\nfirst_day_of_2022 = '2022-01-01'\nfirst_day_of_2023 = '2023-01-01'\n\nlast_day_of_2021.years_started_until(first_day_of_2022)\n# 1\nlast_day_of_2021.years_started_until(first_day_of_2023)\n# 2\nlast_day_of_2021.months_started_until(first_day_of_2022)\n# 1\nlast_day_of_2021.months_started_since(date_assistant_birthday)\n# 4\n```\n",
    'author': 'Jorge Alvarado',
    'author_email': 'alvaradosegurajorge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jalvaradosegura/date_assistant',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
