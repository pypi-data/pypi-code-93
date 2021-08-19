# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_whooshalchemy3']

package_data = \
{'': ['*']}

install_requires = \
['Flask-SQLAlchemy>=2.5.1,<3.0.0',
 'Flask>=1.1',
 'SQLAlchemy>=1.4,<1.4.23',
 'Whoosh>=2.7',
 'blinker>=1.4,<2.0']

setup_kwargs = {
    'name': 'flask-whooshalchemy3',
    'version': '0.3.0',
    'description': 'Whoosh indexing capabilities for Flask-SQLAlchemy, Python 3 compatibility fork.',
    'long_description': '# Flask-WhooshAlchemy3\n[![PyPI version](https://badge.fury.io/py/flask-whooshalchemy3.svg)](https://badge.fury.io/py/flask-whooshalchemy3)\n[![license](https://img.shields.io/github/license/blakev/flask-whooshalchemy3.svg)]()\n\nWhoosh indexing capabilities for Flask-SQLAlchemy, Python 3 compatibility fork.\nPerformance improvements and suggestions are readily welcome.\n\nInspired from gyllstromk\'s [Flask-WhooshAlchemy](https://github.com/gyllstromk/Flask-WhooshAlchemy).\n\n- [Whoosh](http://whoosh.readthedocs.io/en/latest/intro.html)\n- [Flask-SqlAlchemy](http://flask-sqlalchemy.pocoo.org/2.1/)\n\n\n## Install\n\n```bash\n$ pip install flask-whooshalchemy3\n```\n\n..alternatively from source,\n\n```bash\n$ pip install git+git://github.com/blakev/Flask-WhooshAlchemy3.git@master\n```\n\n\n## Quickstart\n\n```python\n\nfrom datetime import datetime\n\nimport flask_sqlalchemy\nimport flask_whooshalchemy3\nfrom whoosh.analysis import StemmingAnalyzer\n\ndb = flask_sqlalchemy.SQLAlchemy()\n\n\nclass BlogPost(db.Model):\n    __tablename__ = \'posts\'\n    __searchable__ = [\'title\', \'content\', \'summary\']  # indexed fields\n    __analyzer__ = StemmingAnalyzer()\n\n    id = db.Column(db.Integer, primary_key=True)\n    title = db.Column(db.String(255), unique=True)\n    content = db.Column(db.Text(32 * 1024))\n    summary = db.Column(db.String(1024))\n    created = db.Column(db.DateTime, default=datetime.utcnow)\n\n```\n\nCommitting model instances to the session will write or update the Whoosh index.\n\n```python\ndb.session.add(BlogPost(title=\'First Post!\', content=\'This is awesome.\'))\ndb.session.commit()\n```\n\nSearching is done via `Model.query.search(..)`. However, the request must be done within the Flask\nrequest context otherwise the database connection may not be established.\n\n```python\n@app.route(\'/posts\')\ndef posts():\n    num_posts = min(request.args.get(\'limit\', 10), 50)\n    query = request.args.get(\'q\', \'\')\n    results = BlogPost.query.search(query, limit=num_posts)\n```\n\n\nResults are ordered by Whoosh\'s ranking-algorithm, but can be overwritten with SQLAlchemy `.order_by`.\n\n```python\nyesterday = datetime.utcnow() - timedelta(days=1)\nresults = BlogPost.query\n            .filter(BlogPost.created > yesterday)\n            .search(\'first\')\n            .order_by(desc(BlogPost.created))\n```\n\n## Flask Configuration\n\n`WHOOSH_ANALYZER` **(whoosh.Analyzer)**\n- Sets the global text analyzer, available options [in Whoosh documentation](http://whoosh.readthedocs.io/en/latest/analysis.html). \n- Default: `StemmingAnalyzer`.\n\n`WHOOSH_INDEX_PATH` (str)\n- File path to where the text indexes will be saved. \n- Default: `{cwd}/.indexes/*`\n\n`WHOOSH_INDEXING_CPUS` (int)\n- The number of system processes to spawn for indexing new and modified documents.\n- Default: `2`\n\n`WHOOSH_INDEXING_RAM` (int)\n- The amount of RAM, in megabytes, to reserve per indexing process for data processing.\n- Default: `256`\n\n`WHOOSH_RAM_CACHE` (bool)\n- Allows common queries and their fields to be stored in cache, in RAM.\n- Default: `False`\n\n## License\n\n```text\nMIT License\n\nCopyright (c) 2017 Blake VandeMerwe\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n```',
    'author': 'Blake VandeMerwe',
    'author_email': 'blakev@null.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/blakev/Flask-WhooshAlchemy3',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
