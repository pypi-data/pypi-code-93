# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dqp']

package_data = \
{'': ['*']}

install_requires = \
['msgpack>=1.0.2,<2.0.0']

setup_kwargs = {
    'name': 'dqp',
    'version': '0.0.5',
    'description': 'A simple library to process a list of messages from disk',
    'long_description': 'Disk Queue Processing\n=====================\n\n\nLibrary to do simple disk based processing of messagepack dictionaries in a file.\n\nAll files are flat files and directories. To manage a simple folder structure with naming convention, use the `Project` class.\n\nFrom the project you can open a source/sink and read/write with them using python dictionaries.\n\nSinks are rotated, sources keep track of a last read entry to allow you to continue later. To do this on close, use the Project class.\n\n```\nfrom dqp.queue import Project\n\nwith Project("/tmp/banana") as project:\n    s = project.open_sink("hello")\n    s.write_dict({"a": 1})\n    s.write_dict({"b": 1})\n    s.write_dict({"c": 1})\n    s.write_dict({"d": 1})\n\nwith Project("/tmp/banana") as project:\n    s = project.continue_source("hello")\n    for filename, index, msg in s:\n        print("1st go:", msg)\n        break\n\nwith Project("/tmp/banana") as project:\n    s = project.continue_source("hello")\n    for filename, index, msg in s:\n        print("2nd go:", msg)\n\n```\n\nQueue files are rotated based on timestamp, so each write_dict does look at the clock to see if we already need to rotate and what the new file path should be.\n\nClean up by telling the source to unlink everything up to last or a given queue filename prefix.\n',
    'author': 'Bram Neijt',
    'author_email': 'bram@neijt.nl',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/bneijt/dqp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
