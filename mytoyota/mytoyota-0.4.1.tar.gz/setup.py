# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mytoyota']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.1.1,<2.0.0', 'httpx>=0.18.1,<0.19.0', 'langcodes>=3.1.0,<4.0.0']

setup_kwargs = {
    'name': 'mytoyota',
    'version': '0.4.1',
    'description': 'Python client for Toyota Connected Services.',
    'long_description': '# Toyota Connected Services Python module\n\n### [!] **This is still in beta**\n\n## Description\n\nPython 3 package to communicate with Toyota Connected Services.\nThis is an unofficial package and Toyota can change their API at any point without warning.\n\n## Installation\n\nThis package can be installed through `pip`.\n\n```text\npip install mytoyota\n```\n\n## Usage\n\n```python\nimport arrow\nimport asyncio\nfrom mytoyota.client import MyT\n\nusername = "jane@doe.com"\npassword = "MyPassword"\nlocale = "da-dk"\n\n# Get supported regions.\nprint(MyT.get_supported_regions())\n\nclient = MyT(username=username, password=password, locale=locale, region="europe")\n\n\nasync def get_information():\n    print("Logging in...")\n    await client.login()\n\n    print("Retrieving cars...")\n    # Returns cars registered to your account + information about each car.\n    cars = await client.get_vehicles()\n\n    for car in cars:\n        # Returns live data from car/last time you used it.\n        vehicle = await client.get_vehicle_status(car)\n        print(vehicle)\n\n        # Stats returned in a dict\n        daily_stats = await client.get_driving_statistics(cars[0][\'vin\'], interval="day")\n        print(daily_stats)\n\n        # Stats returned in json.\n        weekly_stats = await client.get_driving_statistics_json(cars[0][\'vin\'], interval="week")\n        print(weekly_stats)\n\n        # ISO 8601 week stats\n        iso_weekly_stats = await client.get_driving_statistics(cars[0][\'vin\'], interval="isoweek")\n        print(iso_weekly_stats)\n\n        # Monthly stats is returned by default\n        monthly_stats = await client.get_driving_statistics(cars[0][\'vin\'])\n        print(monthly_stats)\n\n        #Get year to date stats.\n        yearly_stats = await client.get_driving_statistics(car[\'vin\'], interval="year")\n        print(yearly_stats)\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(get_information())\nloop.close()\n\n```\n\n## Known issues\n\n- Statistical endpoint will return `None` if no trip have been performed in the requested timeframe. This problem will often happen at the start of each week, month or year. Also daily stats will of course also be unavailable if no trip have been performed.\n- Toyota\'s API can be a little flaky sometimes. So be aware of that when using this in your project.\n\n## Docs\n\nComing soon...\n\n## Contributing\n\nThis python module uses poetry and pre-commit.\n\nTo start contributing, fork this repository and run `poetry install`. Then create a new branch. Before making a PR, please run pre-commit `poetry run pre-commit run --all-files` and make sure that all tests passes locally first.\n\n## Note\n\nAs I [@DurgNomis-drol](https://github.com/DurgNomis-drol) am not a professional programmer. I will try to maintain it as best as I can. If someone is interested in helping with this, they are more the welcome to message me to be a collaborator on this project.\n\n## Credits\n\nA huge thanks go to [@calmjm](https://github.com/calmjm) for making [tojota](https://github.com/calmjm/tojota).\n',
    'author': 'Simon Grud Hansen',
    'author_email': 'simongrud@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DurgNomis-drol/mytoyota',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
