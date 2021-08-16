# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yourtube']

package_data = \
{'': ['*'], 'yourtube': ['failed/*']}

install_requires = \
['ipyevents>=2.0.1,<3.0.0',
 'ipywidgets>=7.6.3,<8.0.0',
 'krakow>=0.1.2,<0.2.0',
 'magic-wormhole>=0.12.0,<0.13.0',
 'matplotlib>=3.4.2,<4.0.0',
 'networkx>=2.6.1,<3.0.0',
 'numpy>=1.21.0,<2.0.0',
 'pickleDB>=0.9.2,<0.10.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.26.0,<3.0.0',
 'scipy>=1.7.0,<2.0.0',
 'sklearn>=0.0,<0.1',
 'tqdm>=4.61.2,<5.0.0',
 'voila>=0.2.10,<0.3.0',
 'youtube-transcript-api>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['yourtube = yourtube.__init__:run',
                     'yourtube-scrape = yourtube.scraping:scrape_all_playlists',
                     'yourtube-scrape-transcripts = '
                     'yourtube.scraping:scrape_transcripts_from_watched_videos',
                     'yourtube-scrape-watched = '
                     'yourtube.scraping:scrape_watched']}

setup_kwargs = {
    'name': 'yourtube',
    'version': '0.6.0',
    'description': 'Better youtube recommendations',
    'long_description': None,
    'author': 'Filip Sondej',
    'author_email': 'filipsondej@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
