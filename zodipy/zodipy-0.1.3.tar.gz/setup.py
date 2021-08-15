# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['zodipy']

package_data = \
{'': ['*']}

install_requires = \
['astropy>=4.3.1,<5.0.0',
 'astroquery>=0.4.3,<0.5.0',
 'healpy>=1.15.0,<2.0.0',
 'numpy>=1.21.1,<2.0.0',
 'scipy>=1.7.1,<2.0.0']

setup_kwargs = {
    'name': 'zodipy',
    'version': '0.1.3',
    'description': 'Zodipy is a python tool that simulates the instantaneous Zodiacal emission as seen from an observer.',
    'long_description': "# Zodipy\n\n## Description\nZodipy is a python tool that simulates the instantaneous Zodiacal emission as seen by an observer.\n\n## Installing\nZodipy is installed with `pip`.\n```bash\npip install zodipy\n```\n\n## Usage\nThe following will produce a HEALPIX map of the simulated Zodiacal emission at\n800 GHz as seen from L2 at 2010-01-01.\n```python\nimport zodipy\nfrom datetime import datetime\n\nzodi = zodipy.Zodi('L2', datetime(2010, 1, 1))\nemission = zodi.get_emission(nside=128, freq=800)\n```\n\nThe simulated emission can be visualized using Healpy and matplotlib.\n```python\nimport healpy as hp\nimport matplotlib.pyplot as plt\n\nhp.mollview(\n    emission, \n    norm='hist', \n    unit='MJy/sr', \n    title='Zodiacal Emission as seen from L2 (2010-01-01)', \n)\nplt.show()\n```\n![plot](imgs/zodi.png)",
    'author': 'Metin San',
    'author_email': 'metinisan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MetinSa/zodipy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
