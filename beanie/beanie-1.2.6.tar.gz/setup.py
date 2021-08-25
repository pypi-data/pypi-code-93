# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['beanie',
 'beanie.executors',
 'beanie.migrations',
 'beanie.migrations.controllers',
 'beanie.odm',
 'beanie.odm.interfaces',
 'beanie.odm.operators',
 'beanie.odm.operators.find',
 'beanie.odm.operators.update',
 'beanie.odm.queries',
 'beanie.odm.utils']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2,<8.0.0',
 'motor>=2.5,<3.0',
 'pydantic>=1.5,<2.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['beanie = beanie.executors.migrate:migrations']}

setup_kwargs = {
    'name': 'beanie',
    'version': '1.2.6',
    'description': 'Asynchronous Python ODM for MongoDB',
    'long_description': '[![Beanie](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/white_bg.svg)](https://github.com/roman-right/beanie)\n\n## Overview\n\n[Beanie](https://github.com/roman-right/beanie) - is an Asynchronous Python\nobject-document mapper (ODM) for MongoDB, based\non [Motor](https://motor.readthedocs.io/en/stable/)\nand [Pydantic](https://pydantic-docs.helpmanual.io/).\n\nWhen using Beanie each database collection has a corresponding `Document` that\nis used to interact with that collection. In addition to retrieving data,\nBeanie allows you to add, update, or delete documents from the collection as\nwell.\n\nBeanie saves you time by removing boiler-plate code and it helps you focus on\nthe parts of your app that actually matter.\n\nData and schema migrations are supported by Beanie out of the box.\n\n## Installation\n\n### PIP\n\n```shell\npip install beanie\n```\n\n### Poetry\n\n```shell\npoetry add beanie\n```\n## Example\n\n```python\nfrom typing import Optional\nfrom pydantic import BaseModel\nfrom beanie import Document, Indexed, init_beanie\nimport asyncio, motor\n\nclass Category(BaseModel):\n    name: str\n    description: str\n\nclass Product(Document):\n    name: str                          # You can use normal types just like in pydantic\n    description: Optional[str] = None\n    price: Indexed(float)              # You can also specify that a field should correspond to an index\n    category: Category                 # You can include pydantic models as well\n\n# Beanie is fully asynchronous, so we will access it from an async function\nasync def example():\n    # Beanie uses Motor under the hood \n    client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://user:pass@host:27017")\n\n    # Init beanie with the Product document class\n    await init_beanie(database=client.db_name, document_models=[Product])\n\n    chocolate = Category(name="Chocolate", description="A preparation of roasted and ground cacao seeds.")\n    # Beanie documents work just like pydantic models\n    tonybar = Product(name="Tony\'s", price=5.95, category=chocolate)\n    # And can be inserted into the database\n    await tonybar.insert() \n    \n    # You can find documents with pythonic syntax\n    product = await Product.find_one(Product.price < 10)\n    \n    # And update them\n    await product.set({Product.name:"Gold bar"})\n    \nasyncio.run(example())\n```\n\n## Links\n\n### Documentation\n\n- **[Doc](https://roman-right.github.io/beanie/)** - Tutorial, API docmentation, and development guidlines.\n\n### Example Projects\n\n- **[fastapi-beanie-jwt](https://github.com/flyinactor91/fastapi-beanie-jwt)** - \n  Sample FastAPI server with JWT auth and Beanie ODM by [Michael duPont](https://github.com/flyinactor91)\n\n### Articles\n\n- **[Announcing Beanie - MongoDB ODM](https://dev.to/romanright/announcing-beanie-mongodb-odm-56e)**\n- **[Build a Cocktail API with Beanie and MongoDB](https://developer.mongodb.com/article/beanie-odm-fastapi-cocktails/)**\n- **[MongoDB indexes with Beanie](https://dev.to/romanright/mongodb-indexes-with-beanie-43e8)**\n- **[Beanie Projections. Reducing network and database load.](https://dev.to/romanright/beanie-projections-reducing-network-and-database-load-3bih)**\n\n### Resources\n\n- **[GitHub](https://github.com/roman-right/beanie)** - GitHub page of the\n  project\n- **[Changelog](https://roman-right.github.io/beanie/changelog)** - list of all\n  the valuable changes\n- **[Discord](https://discord.gg/ZTTnM7rMaz)** - ask your questions, share\n  ideas or just say `Hello!!`\n\n----\nSupported by [JetBrains](https://jb.gg/OpenSource)\n\n[![JetBrains](https://raw.githubusercontent.com/roman-right/beanie/main/assets/logo/jetbrains.svg)](https://jb.gg/OpenSource)\n',
    'author': 'Roman',
    'author_email': 'roman-right@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://roman-right.github.io/beanie/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
