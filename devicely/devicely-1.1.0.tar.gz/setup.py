# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['devicely']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.1,<2.0.0', 'pandas>=1.3.0,<2.0.0', 'pyEDFlib>=0.1.22,<0.2.0']

setup_kwargs = {
    'name': 'devicely',
    'version': '1.1.0',
    'description': 'Read multiple signals from different sources.',
    'long_description': '[![pyOpenSci](https://tinyurl.com/y22nb8up)](https://github.com/pyOpenSci/software-review/issues/37)\n[![PyPI version](https://badge.fury.io/py/devicely.svg)](https://badge.fury.io/py/devicely)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/devicely.svg)](https://pypi.python.org/pypi/devicely/)\n[![Actions Status: test](https://github.com/hpi-dhc/devicely/workflows/test/badge.svg)](https://github.com/hpi-dhc/devicely/actions/workflows/test.yml)\n![Coverage Badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/jostmorgenstern/270a0114dfad9251945a146dd6d29fa6/raw/devicely_coverage_main.json)\n[![DOI](https://zenodo.org/badge/279395106.svg)](https://zenodo.org/badge/latestdoi/279395106)\n[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hpi-dhc/devicely-example/HEAD)\n\n![Devicely Logo](/imgs/logo/devicely-logo.png)\n\nDevicely is a Python package for reading, de-identifying and writing data from various health monitoring sensors.\nWith devicely, you can read sensor data and have it easily accessible in dataframes.\nYou can also de-identify data and write them back using their original data format. This makes it convenient to share sensor data with other researchers while mantaining people\'s privacy.\n\n[Documentation](https://hpi-dhc.github.io/devicely/)\n\n[PyPi](https://pypi.org/project/devicely/)\n\n## Sneak Peek\n\nInstalling devicely is as easy as executing:\n\n`pip install devicely`\n\nAll devices contain the following methods as exemplified through Empatica:\n\n```\nempatica_reader = devicely.EmpaticaReader(path_to_empatica_files)\nempatica_reader.timeshift()\nempatica_reader.write(path_to_write_files)\n```\n\nYou can also try this [notebook](https://github.com/hpi-dhc/devicely-example)\nwith examples and sample data or check our binder:\n\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/hpi-dhc/devicely-example/HEAD)\n\n## Quick Start\n\nTo get started quickly, follow our [quick-start guide](https://hpi-dhc.github.io/devicely/examples.html#).\n\nOr check the full documentation: https://hpi-dhc.github.io/devicely/\n\n\n## Supported Sensors\n\n- [Empatica E4](https://e4.empatica.com/e4-wristband) is a wearable device that offers real-time physiological data acquisition such as blood volume pulse, electrodermal activity (EDA), heart rate, interbeat intervals, 3-axis acceleration and skin temperature.\n\n- [Biovotion Everion](https://www.biovotion.com/everion/) is a wearable device used for the continuous monitoring of vital signs. Currently, it measures the following vital signs: heart rate, blood pulse wave, heart rate variability, activity, SPO2, blood perfusion, respiration rate, steps, energy expenditure, skin temperature, EDA / galvanic skin response (GSR), barometric pressure and sleep.\n\n- [1-lead ECG monitor Faros<sup>TM</sup> 180 from Bittium](https://shop.bittium.com/product/36/bittium-faros-180-solution-pack) is a one channel ECG monitor with sampling frequency up to 1000 Hz and a 3D acceleration sampling up to 100Hz.\n\n- [Spacelabs (SL 90217)](https://www.spacelabshealthcare.com/products/diagnostic-cardiology/abp-monitoring/90217a/) is an oscillometric blood pressure (BP) monitor which can be used to automatically track a person\'s BP in specificed time intervals.\n\n- [TimeStamp for Android](https://play.google.com/store/apps/details?id=gj.timestamp&hl=en) allows you to record the timestamp of an event at the time it occurs. It also allows you to create specific tags such as "Running" or "Walking" and timestamp those specific activities.\n\n- [Shimmer Consensys GSR](https://www.shimmersensing.com/products/gsr-optical-pulse-development-kit#specifications-tab) is a device that is used to collect sensor data in real time and it contains sensors such as GSR / EDA, photoplethysmography (PPG), 3-axis accelerometer, 3-axis gyroscope, 3-axis magnetometer & integrated altimeter.\n\n## How to Contribute\n\nIf you want to be part of this mission, please check our documentation on how to contribute [here](https://hpi-dhc.github.io/devicely/contribution.html).\n\n## Authors\n\n```\n* Ariane Sasso\n* Jost Morgenstern\n* Felix Musmann\n* Bert Arnrich\n```\n\n## Contributors\n\n```\n* Arpita Kappattanavar\n* Bjarne Pfitzner\n* Lin Zhou\n* Pascal Hecker\n* Philipp Hildebrandt\n* Sidratul Moontaha\n```\n',
    'author': 'Ariane Morassi Sasso',
    'author_email': 'ariane.morassi-sasso@hpi.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hpi-dhc/devicely',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
