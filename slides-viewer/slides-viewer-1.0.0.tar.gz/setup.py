# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slides_viewer', 'slides_viewer.player', 'slides_viewer.playlist']

package_data = \
{'': ['*']}

install_requires = \
['jsonschema>=3.2.0,<4.0.0', 'pyside2==5.15.2']

entry_points = \
{'console_scripts': ['slides-viewer = slides_viewer.console:main']}

setup_kwargs = {
    'name': 'slides-viewer',
    'version': '1.0.0',
    'description': 'Viewer for live presentations, based on manim-presentation for now',
    'long_description': '# Slides Viewer\n\nViewer for live presentations, based on [manim-presentation](https://github.com/galatolofederico/manim-presentation) *for now*.\n\n\n\n### License\n\nThe code is released as Free Software under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html) license.',
    'author': 'Vincent Lafeychine',
    'author_email': 'vincent.lafeychine@gmail.com',
    'maintainer': 'Vincent Lafeychine',
    'maintainer_email': 'vincent.lafeychine@gmail.com',
    'url': 'https://github.com/lafeychine/slides-viewer/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
