# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyknp',
 'pyknp.evaluate',
 'pyknp.juman',
 'pyknp.knp',
 'pyknp.scripts',
 'pyknp.utils']

package_data = \
{'': ['*']}

install_requires = \
['six']

entry_points = \
{'console_scripts': ['knp-drawtree = pyknp.scripts.knp_drawtree:main']}

setup_kwargs = {
    'name': 'pyknp',
    'version': '0.5.2',
    'description': 'Python module for JUMAN/KNP',
    'long_description': '# pyknp: Python Module for JUMAN++/KNP\n\n形態素解析器JUMAN++(JUMAN)と構文解析器KNPのPythonバインディング (Python2系と3系の両方に対応)。\n\n## Requirements\n- Python\n    - Verified Versions: 2.7.15,  3.7.11\n- 形態素解析器 [JUMAN++](http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN++) [[EN](http://nlp.ist.i.kyoto-u.ac.jp/EN/index.php?JUMAN++)]\n(or [JUMAN](http://nlp.ist.i.kyoto-u.ac.jp/index.php?JUMAN)[[EN](http://nlp.ist.i.kyoto-u.ac.jp/EN/index.php?JUMAN)])\n    - JUMAN++ はJUMANの後継にあたる形態素解析器\n- 構文解析器 [KNP](http://nlp.ist.i.kyoto-u.ac.jp/index.php?KNP) [[EN](http://nlp.ist.i.kyoto-u.ac.jp/EN/index.php?KNP)]\n\n## Installation\n```\n$ pip install pyknp\n```\n\n## Documents\nhttps://pyknp.readthedocs.io/en/latest/\n\n\n## Authors/Contact\n京都大学 黒橋・河原研究室 (contact@nlp.ist.i.kyoto-u.ac.jp)\n- John Richardson, Tomohide Shibata, Yuta Hayashibe, Tomohiro Sakaguchi\n',
    'author': 'Kurohashi-Kawahara Lab, Kyoto Univ',
    'author_email': 'contact@nlp.ist.i.kyoto-u.ac.jp',
    'maintainer': 'Nobuhiro Ueda',
    'maintainer_email': 'ueda@nlp.ist.i.kyoto-u.ac.jp',
    'url': 'https://github.com/ku-nlp/pyknp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
