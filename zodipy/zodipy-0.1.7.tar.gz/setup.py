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
    'version': '0.1.7',
    'description': 'Zodipy is a python tool that simulates the Zodiacal emission.',
    'long_description': "[![PyPI version](https://badge.fury.io/py/zodipy.svg)](https://badge.fury.io/py/zodipy)\n[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)\n\n# Zodipy\n\n## Description\nZodipy is a python tool that simulates the Zodiacal emission.\n\n## Installing\nZodipy is installed with `pip`.\n```bash\npip install zodipy\n```\n\n## Usage\nThe following examples are meant to provide an overview of how Zodipy may be\nused to produce simulations of the Zodiacal emission. A more in-depth\ndocumentation will be available in the near future.\n\n## Simulating the instantaneous emission from a single observation\nThe simplest use case of Zodipy is to simulate the instantaneous emission as\nseen from a major body or a location in the Solar system, as of today:\n```python\nimport zodipy\n\nzodi = zodipy.Zodi()\nemission = zodi.get_emission(nside=128, freq=800)\n```\nCalling the `Zodi` object with no arguments will by default set up the initial\nconditions of the simulation for an observer at L2 today. The `get_emission`\nmethod of the `Zodi` object, is then called to simulate and return the emission\nfor a given nside and frequency. \n\nWe can visualize the above simulated emission using Healpy:\n\n![plot](imgs/zodi_default.png)\n\nAlternatively, a specific observer and specific epochs can be passed as\narguments to the `Zodi` object. The `epochs` object must match one of the\npossible formats defined in [astroquery's JPL Horizons\napi](https://astroquery.readthedocs.io/en/latest/jplhorizons/jplhorizons.html).\n\n```python\nimport zodipy\n\nMJD = 59215  # 2010-01-01 in Modified Julian dates\nzodi = zodipy.Zodi(observer='Planck', epochs=MJD)\nemission = zodi.get_emission(nside=128, freq=800)\n```\n![plot](imgs/zodi_planck.png)\n\nTo return the component-wise emission the keyword `return_comps` in the\n`get_emission` function may be set to True.\n\n## Simulating the pixel weighted average over multiple observations\nBy providing multiple dates in the `epochs` argument to `Zodi`, the\n`get_emission` function will return the emission averaged over all observations.\n\nIt is possible to provide hit maps for each respective observation given by\n`epochs`. This is done by passing a sequence of hit maps through the `hit_maps`\nargument in `Zodi`. \n\nBelow is an example where we simulate the\npixel weighted average over daily observations over a year:\n```python\nimport zodipy\n\nepochs = {\n    'start': '2010-01-01', \n    'stop': '2011-01-01', \n    'step' : '1d'\n}\nhit_maps = ... # Your sequence of hit_maps for each observation in epochs \n\nzodi = zodipy.Zodi(observer='Planck', epochs=epochs, hit_maps=hit_maps)\nemission = zodi.get_emission(nside=128, freq=800)\n```\n![plot](imgs/zodi_planck_weighted.png)\n\nThis simulation closely resembles map making in the time-ordered domain, with\nthe hit maps playing a significant role on the outputted emission due to the\nmotion of Earth through the interplanetary dust.\n\nThe hit maps used in the above example was somewhat arbitrarily chosen (stripes\nof 10 degrees perpendicular to the ecliptic).\n\n## Interplanetary dust models\nZodipy uses the [Kelsall et al.\n(1998)](https://ui.adsabs.harvard.edu/abs/1998ApJ...508...44K/abstract)\nInterplanetary dust model. The line-of-sight integrals are computed using the\ndefinition in [Planck 2013 results. XIV. Zodiacal\nemission](https://arxiv.org/abs/1303.5074). During the Planck analysis, three\ndifferent sets of emissivities were fit to describe the emission. These can be\nselected by providing the keyword argument `model` to the `Zodi` object:\n```python\nimport zodipy\n\nzodi = zodipy.Zodi(model='planck 2013')\n```\nThe available models are 'planck 2013', 'planck 2015', and 'planck 2018'. The\ndefault is the 2018 model. Note that selecting the 2013 model will include the\nCircumsolar and Earth-trailing components, which were left out in the 2015 and\n2018 Planck analyses.",
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
