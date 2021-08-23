# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uquake',
 'uquake.core',
 'uquake.core.util',
 'uquake.grid',
 'uquake.imaging',
 'uquake.io',
 'uquake.io.event',
 'uquake.io.grid',
 'uquake.io.waveform',
 'uquake.nlloc',
 'uquake.waveform']

package_data = \
{'': ['*']}

install_requires = \
['dynaconf>=3.1.4,<4.0.0',
 'h5py>=3.2.1,<4.0.0',
 'ipython>=7.19.0,<8.0.0',
 'jedi==0.17.2',
 'loguru>=0.5.3,<0.6.0',
 'numpy>=1.18.0,<2.0.0',
 'obspy>=1.2.2,<2.0.0',
 'openpyxl>=3.0.6,<4.0.0',
 'pandas>=1.2.1,<2.0.0',
 'pytest>=6.2.1,<7.0.0',
 'scikit-fmm>=2021.2.2,<2022.0.0',
 'tqdm>=4.59.0,<5.0.0',
 'utm>=0.7.0,<0.8.0',
 'vtk>=9.0.1,<10.0.0']

entry_points = \
{'uquake.io.event': ['NLLOC = uquake.io.nlloc', 'QUAKEML = uquake.io.quakeml'],
 'uquake.io.grid': ['CSV = uquake.io.grid',
                    'NLLOC = uquake.io.grid',
                    'PICKLE = uquake.io.grid',
                    'VTK = uquake.io.grid'],
 'uquake.io.grid.CSV': ['readFormat = uquake.io.grid:read_csv',
                        'writeFormat = uquake.io.grid:write_csv'],
 'uquake.io.grid.PICKLE': ['readFormat = uquake.io.grid:read_pickle',
                           'writeFormat = uquake.io.grid:write_pickle'],
 'uquake.io.grid.VTK': ['readFormat = uquake.io.grid:read_vtk',
                        'writeFormat = uquake.io.grid:write_vtk'],
 'uquake.io.site.CSV': ['readFormat = uquake.io.site:read_csv',
                        'writeFormat = uquake.io.site:write_csv'],
 'uquake.io.site.PICKLE': ['readFormat = uquake.io.site:read_pickle',
                           'writeFormat = uquake.io.site:write_pickle'],
 'uquake.io.waveform': ['ESG_SEGY = uquake.io.waveform',
                        'HSF = micorquake.io.waveform',
                        'IMS_ASCII = uquake.io.waveform',
                        'IMS_CONTINUOUS = uquake.io.waveform',
                        'TEXCEL_CSV = uquake.io.waveform'],
 'uquake.io.waveform.ESG_SEGY': ['readFormat = '
                                 'uquake.io.waveform:read_ESG_SEGY'],
 'uquake.io.waveform.IMS_ASCII': ['readFormat = '
                                  'uquake.io.waveform:read_IMS_ASCII'],
 'uquake.io.waveform.TEXCEL_CSV': ['readFormat = '
                                   'uquake.io.waveform:read_TEXCEL_CSV']}

setup_kwargs = {
    'name': 'uquake',
    'version': '0.7.0',
    'description': 'extension of the ObsPy library for local seismicity',
    'long_description': None,
    'author': 'uQuake development team',
    'author_email': 'dev@uQuake.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
