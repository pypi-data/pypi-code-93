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
    'version': '0.1.2',
    'description': 'A library for assigning Norwegian metadata to coordinates',
    'long_description': '# Hvor\n\nHar du en eller flere koordinater innenfor Norges geografiske grenser som du\ngjerne skulle visst mer om? `hvor` er et Python-bibliotek for å hente ut ulike\ntyper data for koordinater i Norge. Vi baserer oss på bruk av `pandas` og\n`geopandas`. Data som kan hentes inkluderer:\n\n- Kommunedata (kommune og kommunenummer)\n- Fylkesdata (fylke og fylkesnummer)\n\nFlere typer data vil bli lagt til etterhvert!\n\n## Installering\n\nSå enkelt som\n\n```\npip install hvor\n```\n\n## Bruk\n\nFor et enkeltpunkt med latitude og longitude, bruk `point`\n\n```python\n>>> from hvor import point\n>>> point(61.7327867684485, 5.540150406971685)\n{\'kommunenumer\': [4602], \'kommune\': [\'Kinn\'], \'fylkesnummer\': [46], \'fylke\': [\'Vestland\']}\n```\n\nFor flere koordinater, igjen med latitude og longitude, bruk `points` (merk\n**s** på slutten)\n\n```python\n>>> from hvor import points\n>>> coordinates = {"lat": [63.414109, 69.14579124011655], "lon": [10.416230, 18.15361374220361]}\n>>> points(coordinates)\n{\'kommunenummer\': [5001, 5419], \'kommune\': [\'Trondheim\', \'Sørreisa\'], \'fylkesnummer\': [50, 54], \'fylke\': [\'Trøndelag\', \'Troms og Finnmark\']}\n```\n\nVipps, så har du kommune- og fylkesdata for koordinatene. (\\*men kun hvis\nnøklene dine for bredde- og lengdegrad dine het `lat` og `lon`😅).\n\n## Credits\n\nTusen takk til\n\n- [robhop](https://github.com/robhop) for deling av kommune- og fylkesdata.\n- Kartverket for offentliggjøring av kartdata som robhop baserte seg på.\n',
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
