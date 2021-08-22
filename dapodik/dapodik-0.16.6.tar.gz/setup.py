# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dapodik',
 'dapodik.auth',
 'dapodik.customrest',
 'dapodik.gtk',
 'dapodik.peserta_didik',
 'dapodik.rest',
 'dapodik.rombongan_belajar',
 'dapodik.sarpras',
 'dapodik.sekolah',
 'dapodik.utils',
 'dapodik.validasi']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.2.0,<22.0.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'cachetools>=4.2.2,<5.0.0',
 'cattrs>=1.8.0,<2.0.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['dapodik = dapodik.__main__:main']}

setup_kwargs = {
    'name': 'dapodik',
    'version': '0.16.6',
    'description': 'SDK python untuk aplikasi dapodik.',
    'long_description': "# dapodik\n\n[![dapodik - PyPi](https://img.shields.io/pypi/v/dapodik)](https://pypi.org/project/dapodik/)\n[![Supported Python versions](https://img.shields.io/pypi/pyversions/dapodik)](https://pypi.org/project/dapodik/)\n[![LISENSI](https://img.shields.io/github/license/dapodix/dapodik)](https://github.com/dapodix/dapodik/blob/master/LISENSI)\n[![Donate Saweria](https://img.shields.io/badge/Donasi-Saweria-blue)](https://saweria.co/hexatester)\n[![Tutorial](https://img.shields.io/badge/Tutorial-Penggunaan-informational)](https://github.com/dapodix/dapodik/wiki)\n[![Tests](https://github.com/dapodix/dapodik/workflows/Tests/badge.svg)](https://github.com/dapodix/dapodik/actions?query=workflow%3ATests)\n[![codecov](https://codecov.io/gh/dapodix/dapodik/branch/master/graph/badge.svg)](https://codecov.io/gh/dapodix/dapodik)\n[![Code Style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nSDK python untuk aplikasi dapodik.\n\n## Install\n\nPastikan [python 3.7+](https://www.python.org/ftp/python/3.7.9/python-3.7.9-amd64.exe) terinstall,\nkemudian jalankan perintah di bawah dalam Command Prompt atau Powershell (di Windows + X):\n\n```bash\npip install --upgrade dapodik\n```\n\n## Penggunaan\n\nContoh pennggunaan\n\n```python\nfrom dapodik import Dapodik\n\nemail = 'email@saya.com'\npassword = 'password dapodik'\n\nd = Dapodik(email, password)\nsekolah = d.sekolah()\ndaftar_peserta_didik = d.peserta_didik(sekolah_id=sekolah.sekolah_id)\nfor peserta_didik in daftar_peserta_didik:\n    print(peserta_didik.nama)\n```\n\n## Legal / Hukum\n\nKode ini sama sekali tidak berafiliasi dengan, diizinkan, dipelihara, disponsori atau didukung oleh [Kemdikbud](https://kemdikbud.go.id/) atau afiliasi atau anak organisasinya. Ini adalah perangkat lunak yang independen dan tidak resmi. _Gunakan dengan risiko Anda sendiri._\n",
    'author': 'hexatester',
    'author_email': 'habibrohman@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://dapodix.github.io/dapodik',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
