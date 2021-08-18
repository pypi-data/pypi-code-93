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
    'version': '0.1.5',
    'description': 'Zodipy is a python tool that simulates the instantaneous Zodiacal emission as seen from an observer.',
    'long_description': "[![PyPI version](https://badge.fury.io/py/zodipy.svg)](https://badge.fury.io/py/zodipy)\n[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)\n\n# Zodipy\n\n## Description\nZodipy is a python tool that simulates the instantaneous Zodiacal emission as\nseen by an observer.\n\n## Installing\nZodipy is installed with `pip`.\n```bash\npip install zodipy\n```\n\n## Examples\nThe following examples provides an overview of how Zodipy may be used to produce\nvarious simulations of the Zodiacal emission.\n\n## Simulating a single observation\nThe simplest use case of Zodipy is to simulate the instantaneous emission as\nseen from the Earth-Sun Lagrange point 2, as of today (This is the default\nbehavior of the `Zodi` object):\n```python\nimport zodipy\n\nzodi = zodipy.Zodi()\nemission = zodi.get_emission(nside=128, freq=800)\n```\nWe started by initializing the `Zodi` object with default arguments, after which\nwe have called the `get_emission` method of the `Zodi` object, which simulates\nthe emission at a given map resolution (nside) and frequency. \n\nWe can visualize the emission using Healpy:\n\n![plot](imgs/zodi_default.png)\n\nAlternatively, a specific observer, and a date (`datetime` object) can be passed\nas arguments to the `Zodi` object, which initializes the new configuration:\n```python\nimport zodipy\nfrom datetime import datetime\n\nzodi = zodipy.Zodi('Planck', datetime(2010, 1, 1))\nemission = zodi.get_emission(nside=128, freq=800)\n```\n![plot](imgs/zodi_planck.png)\n\nIt is possible to return the Zodiacal emission component-wise by setting the\nkeyword `return_comps` in the `get_emission` function to True.\n\n## Masked observations\nWe can specify the angle between the observer and the Sun for which all pixels\nare masked out. This is done in the `get_emission` function by providing the\nkeyword argument `solar_cut`, which takes in an angle. In the following we\nattempt to mimic typical satellite scanning strategies by masking out all pixels\nthat look inwards towards the Sun:\n```python\nimport zodipy\nfrom datetime import datetime\n\nzodi = zodipy.Zodi('Planck', datetime(2010, 1, 1))\nemission = zodi.get_emission(nside=128, freq=800, solar_cut=90)\n```\n![plot](imgs/zodi_planck_masked.png)\n\n## Simulating the mean over multiple observations\nWe can simulate the mean emission over a set of observations by initializing the\n`Zodi` object with the following keywords:\n```python\nimport zodipy\nfrom datetime import datetime\n\nzodi = zodipy.Zodi(\n    observer='Planck', \n    start=datetime(2010, 1, 1), \n    stop=datetime(2011, 1, 1), \n    step='10d'\n)\nemission = zodi.get_emission(nside=128, freq=800, solar_cut=90)\n```\nHere we take the mean of linearly spaced observations from 2010-01-01 to\n2011-01-01 with a step size of 10 days (note that this is a more expensive\noperation and may take up to a few minutes depending on the map resolution and\nnumber of observations). ![plot](imgs/zodi_planck_masked_mean.png)\n\n## Interplanetary dust models\nZodipy uses the [Kelsall et al.\n(1998)](https://ui.adsabs.harvard.edu/abs/1998ApJ...508...44K/abstract)\nInterplanetary dust model. The line-of-sight integrals are computed using the\ndefinition in [Planck 2013 results. XIV. Zodiacal\nemission](https://arxiv.org/abs/1303.5074). During the Planck analysis, three\ndifferent sets of emissivities were fit to describe the emission. These can be\nselected by providing the keyword argument `model` to the `Zodi` object:\n```python\nimport zodipy\n\nzodi = zodipy.Zodi(model='planck 2013')\n```\nThe available models are 'planck 2013', 'planck 2015', and 'planck 2018'. The\ndefault is the 2018 model. Note that selecting the 2013 model will include the\nCircumsolar and Earth-trailing components, which were left out in the 2015 and\n2018 Planck analyses.",
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
