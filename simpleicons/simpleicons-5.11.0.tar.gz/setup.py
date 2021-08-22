# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simpleicons', 'simpleicons.icons']

package_data = \
{'': ['*']}

extras_require = \
{'auto-update': ['semantic-version>=2.8.5,<3.0.0',
                 'requests>=2.25.1,<3.0.0',
                 'GitPython>=3.1.18,<4.0.0'],
 'imaging': ['reportlab>=3.5.68,<4.0.0',
             'Pillow>=8.3.1,<9.0.0',
             'svglib>=1.1.0,<2.0.0']}

setup_kwargs = {
    'name': 'simpleicons',
    'version': '5.11.0',
    'description': 'Use a wide-range of icons derived from the simple-icons/simple-icons repo in python.',
    'long_description': '<h1>\n  <img src="logo.svg" alt="Logo" width="50" height="50">\n  simpleicons\n</h1>\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nUse a wide-range of icons derived from the [simple-icons](https://github.com/simple-icons/simple-icons) repo in python. Go to [their website](https://simpleicons.org/) for a full list of icons. The slug version must be used for the `icon_name`. The icons folder that accompanies the package has all the files. The package uses the latest verison of [Simple Icons](https://github.com/simple-icons/simple-icons/releases/latest). It does **not** depend on the filesystem.\n\n## Installation\n\nInstall with `pip install simpleicons`. Keep in mind that this is a fairly large package due to all the icons.\n\n## Usage\n\n### General Usage\n\nThe API can then be used as follows, where [ICON SLUG] is replaced by a slug:\n\n```py\nfrom simpleicons.all import icons\n\n# Get a specific icon by its slug as:\nicons.get(\'[ICON SLUG]\')\n\n# For example:\nicon = icons.get(\'simpleicons\')\n\nprint(icon.__dict__)\n\n"""\n{\n    \'title\': \'Simple Icons\',\n    \'slug\': \'simpleicons\',\n    \'hex\': \'111111\',\n    \'source\': \'https://simpleicons.org/\',\n    \'svg\': \'<svg role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">...</svg>\',\n    \'path\': \'M12 12v-1.5c-2.484 ...\',\n    \'guidelines\': \'https://simpleicons.org/styleguide\',\n    \'license\': {\n        type: \'...\',\n        url: \'https://example.com/\'\n    }\n}\n"""\n```\n\nNOTE: The `guidelines` entry will be `None` if we do not yet have guidelines data for the icon.\n\nNOTE: The `license` entry will be `None` if we do not yet have license data for the icon.\n\nAlternatively you can import the needed icons individually, where [ICON SLUG] is replaced by a slug:\n\n```py\n# Import a specific icon by its slug as:\nfrom simpleicons.icons.[ICON SLUG] import [ICON_SLUG]_icon\n\n# For example:\nfrom simpleicons.icons.simpleicons import simpleicons_icon\n```\n\nLastly, the `icons` object is also enumerable. This is useful if you want to do a computation on every icon:\n\n```py\nfrom simpleicons.all import icons\n\nfor (key, icon in icons) {\n    # do stuff\n}\n```\n\n### XML\n\nThe XML for each icon can be easily manipulated with either of two functions:\n\n`Icon.get_xml(**attrs) -> ElementTree`\n\n```py\nfrom simpleicons.icons.simpleicons import simpleicons_icon\n\n# blue logo, adds the fill attribute: <svg fill="blue"></svg>\nsimpleicons_icon.get_xml(fill="blue")\n```\n\n`Icon.get_xml_bytes(**attrs) -> bytes`\n\n```py\nfrom simpleicons.icons.simpleicons import simpleicons_icon\n\nsimpleicons_icon.get_xml_bytes(fill="blue")\n```\n\n### Image\n\nIn order to use this, you must install the extras: `pip install -e simpleicons[imaging]` . Icons can be converted to PIL Images with `icon_to_image(icon_xml: bytes, bg: int=0xffffff, scale: Tuple[int, int]=(1, 1)) -> Image`:\n\n```py\nfrom simpleicons.icons.simpleicons import simpleicons_icon\nfrom simpleicons.image import icon_to_image\n\nxml_bytes = simpleicons_icon.get_xml_bytes(fill="blue")\n\n# black background and 5x scale\nimg = icon_to_image(xml_bytes, bg=0x000000, scale=(5, 5))\n\n# manipulate PIL Image\nimg.putalpha(32)\nimg.save("simpleicons_blue.png")\n```\n',
    'author': 'Sachin Raja',
    'author_email': 'sachinraja2349@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sachinraja/simpleicons',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
