# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cosmoglobe',
 'cosmoglobe.chain',
 'cosmoglobe.plot',
 'cosmoglobe.sky',
 'cosmoglobe.utils']

package_data = \
{'': ['*'],
 'cosmoglobe': ['data/autoparams.json',
                'data/autoparams.json',
                'data/autoparams.json',
                'data/autoparams.json',
                'data/autoparams.json',
                'data/autoparams.json',
                'data/planck_cmap.dat',
                'data/planck_cmap.dat',
                'data/planck_cmap.dat',
                'data/planck_cmap.dat',
                'data/planck_cmap.dat',
                'data/planck_cmap.dat',
                'data/planck_cmap_logscale.dat',
                'data/planck_cmap_logscale.dat',
                'data/planck_cmap_logscale.dat',
                'data/planck_cmap_logscale.dat',
                'data/planck_cmap_logscale.dat',
                'data/planck_cmap_logscale.dat',
                'data/radio_catalog.dat',
                'data/radio_catalog.dat',
                'data/radio_catalog.dat',
                'data/radio_catalog.dat',
                'data/radio_catalog.dat',
                'data/radio_catalog.dat',
                'data/spdust2_cnm.dat',
                'data/spdust2_cnm.dat',
                'data/spdust2_cnm.dat',
                'data/spdust2_cnm.dat',
                'data/spdust2_cnm.dat',
                'data/spdust2_cnm.dat',
                'data/wmap_cmap.dat',
                'data/wmap_cmap.dat',
                'data/wmap_cmap.dat',
                'data/wmap_cmap.dat',
                'data/wmap_cmap.dat',
                'data/wmap_cmap.dat']}

install_requires = \
['astropy>=4.3.1,<5.0.0',
 'cmasher>=1.6.2,<2.0.0',
 'h5py>=3.4.0,<4.0.0',
 'healpy>=1.15.0,<2.0.0',
 'matplotlib>=3.4.3,<4.0.0',
 'numpy>=1.21.2,<2.0.0',
 'scipy>=1.7.1,<2.0.0',
 'tqdm>=4.62.2,<5.0.0']

setup_kwargs = {
    'name': 'cosmoglobe',
    'version': '0.9.3',
    'description': 'cosmoglobe is a python package that interfaces the Cosmoglobe Sky Model with commander3 outputs for the purpose of producing astrophysical sky maps.',
    'long_description': None,
    'author': 'Metin San',
    'author_email': 'metinisan@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
