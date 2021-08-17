# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hvor']

package_data = \
{'': ['*'], 'hvor': ['resources/*']}

install_requires = \
['Rtree>=0.9.7,<0.10.0',
 'geopandas>=0.9.0,<0.10.0',
 'setuptools>=57.4.0,<58.0.0']

setup_kwargs = {
    'name': 'hvor',
    'version': '0.1.1',
    'description': 'A library for assigning Norwegian metadata to coordinates',
    'long_description': "# Hvor\n\nA library for assigning Norwegian metadata to coordinates. For example, if you\nhave a list of coordinates, and you'd like to know which county and municipality\neach coordinate belongs to, `hvor` can help you.\n\n## Installation\n\nSimply run\n\n```\npip install hvor\n```\n\n## Usage\n\n```python\nfrom hvor import add_metadata_columns_to_df\n\ndf = add_metadata_columns_to_df(df)\n```\n\nVoila! County and municipality metadata for your coordinates have been added to\nyour dataframe (\\*but only if your latitude and longitude columns were called\n`lat` and `lon`😅).\n\n## Credits\n\nBig thanks to [robhop](https://github.com/robhop) for sharing his lightly\nprocessed county and municipality polygons. Also big thanks to Kartverket, for\nsupplying the original dataset.\n",
    'author': 'Espen Hafstad Solvang',
    'author_email': 'espenhafstadsolvang@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bkkas/iout_foss',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
