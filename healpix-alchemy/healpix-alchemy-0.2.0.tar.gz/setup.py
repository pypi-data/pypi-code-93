# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['healpix_alchemy', 'healpix_alchemy.tests']

package_data = \
{'': ['*']}

install_requires = \
['astropy', 'astropy_healpix', 'mocpy', 'sqlalchemy']

setup_kwargs = {
    'name': 'healpix-alchemy',
    'version': '0.2.0',
    'description': 'SQLAlchemy extensions for HEALPix spatially indexed astronomy data',
    'long_description': "# HEALPix Alchemy\n\nThe `healpix_alchemy` Python package extends [SQLAlchemy] will provide spatial\nindexing for astronomical sky coordinates, regions, and raster images (e.g.\nLIGO/Virgo and Fermi probability sky maps) in a relational database. It does\nnot rely on any database extensions.\n\nThis package is a work in progress. Initially, `healpix_alchemy` focuses on\nspatial indexing of point clouds while we work out the SQLAlchemy abstraction\ndesign. Once this is mature, we will incorporate the raster indexing strategies\nfrom https://github.com/growth-astro/healpix-intersection-example.\n\n## Installation\n\nYou can install `healpix_alchemy` the Python Package Index:\n\n    $ pip install healpix-alchemy\n\n## Usage\n\n```python\nfrom healpix_alchemy.point import Point\nfrom sqlalchemy.ext.declarative import declarative_base\n\nBase = declarative_base()\n\n\n# Create two tables Catalog1 and Catalog2 that both have spherical coordinates.\n\nclass Catalog1(Point, Base):\n    __tablename__ = 'catalog1'\n    id = Column(Integer, primary_key=True)\n\n\nclass Catalog2(Point, Base):\n    __tablename__ = 'catalog2'\n    id = Column(Integer, primary_key=True)\n\n\n...\n\n# Populate Catalog1 and Catalog2 tables with some sample data...\nsession.add(Catalog1(id=0, ra=320.5, dec=-23.5))\n...\nsession.add(Catalog2(id=0, ra=18.1, dec=18.3))\n...\nsession.commit()\n\n\n# Cross-match the two tables.\nseparation = 1  # separation in degrees\nquery = session.query(\n    Catalog1.id, Catalog2.id\n).join(\n    Catalog2,\n    Catalog1.within(point, separation)\n).order_by(\n    Catalog1.id, Catalog2.id\n)\nfor row in query:\n    ...  # do something with the query results\n\n\n# Do a cone search around literal ra, dec values.\nseparation = 1  # separation in degrees\npoint = Point(ra=212.5, dec=-33.2)\nquery = session.query(\n    Catalog1.id\n).filter(\n    Catalog1.within(point, separation)\n).order_by(\n    Catalog1.id\n)\nfor row in query:\n    ...  # do something with the query results\n```\n\n[SQLAlchemy]: https://www.sqlalchemy.org\n",
    'author': 'Leo Singer',
    'author_email': 'leo.singer@ligo.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/skyportal/healpix-alchemy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
