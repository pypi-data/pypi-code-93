# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['image_preview_thumbnailer']
install_requires = \
['Pillow>=8.3.1,<9.0.0',
 'beautifulsoup4>=4.8.2,<5.0.0',
 'requests>=2.22.0,<3.0.0']

setup_kwargs = {
    'name': 'pelican-plugin-image-preview-thumbnailer',
    'version': '1.0.0',
    'description': 'Pelican plugin that insert thumbnails along image links',
    'long_description': '[![Pull Requests Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat)](http://makeapullrequest.com)\n[![build status](https://github.com/pelican-plugins/image-preview-thumbnailer/workflows/build/badge.svg)](https://github.com/pelican-plugins/image-preview-thumbnailer/actions?query=workflow%3Abuild)\n[![Pypi latest version](https://img.shields.io/pypi/v/pelican-plugin-image-preview-thumbnailer.svg)](https://pypi.python.org/pypi/pelican-plugin-image-preview-thumbnailer)\n[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)\n\n[Pelican](https://getpelican.com) plugin that insert thumbnails along image links.\n\n## Démo page\n<https://chezsoi.org/lucas/blog/pages/images-libres-de-droits.html#fonts>\n\nSource Markdown: [pages/images-libres-de-droits.md](https://github.com/Lucas-C/ludochaordic/blob/master/content/pages/images-libres-de-droits.md)\n\n## Usage instructions\nTo enable this plugin:\n1. Install the package from Pypi: `pip install pelican-plugin-image-preview-thumbnailer`\n2. Add the plugin to your `pelicanconf.py`:\n```python\nPLUGINS = [..., \'image_preview_thumbnailer\']\n```\n3. Enable it on the article / pages you wish by inserting this piece of metadata:\n```yaml\nImage-preview-thumbnailer: $selector\n```\n\n`$selector` is a CSS selector to target HTML elements this plugin will parse and look for `<a>` hyperlinks.\nIt can be for example `article` if your Pelican template place your pages content in `<article>` tags,\nor just `body` to select the whole page.\n\n### Supported link formats\nCurrently this plugin support preview of the following links:\n* "raw" links to GIF/JPEG/PNG images\n* links to **ArtStation** artwork pages\n* links to **DeviantArt** artwork pages\n* links to **Wikipedia/Wikimedia** images\n\nFeel free to submit PRs to add support for more image hosting websites.\n\n### Configuration\nAvailable options:\n\n- `IMAGE_PREVIEW_THUMBNAILER_INSERTED_HTML` (optional, default: `\'<img src="{thumb}">\'`) :\n  the HTML code to be inserted after every link (`<a>`) to an image, in order to preview it\n- `IMAGE_PREVIEW_THUMBNAILER_DIR` (optional, default: `thumbnails`) :\n  directory where thumbnail images are stored\n- `IMAGE_PREVIEW_THUMBNAILER_THUMB_SIZE` (optional, default: `300`) :\n  size in pixel of the generated thumbnails.\n- `IMAGE_PREVIEW_THUMBNAILER_ENCODING` (optional, default: `utf-8`) :\n  encoding to use to parse HTML files\n- `IMAGE_PREVIEW_THUMBNAILER_HTML_PARSER` (optional, default: `html.parser`) :\n  parse that BEautifulSoup will use to parse HTML files\n- `IMAGE_PREVIEW_THUMBNAILER_CERT_VERIFY` (optional, default: `False`) :\n  enforce HTTPS certificates verification when sending linkbacks\n- `IMAGE_PREVIEW_THUMBNAILER_REQUEST_TIMEOUT` (optional, in seconds, default: `3`) :\n  time in seconds allowed for each HTTP linkback request before abandon\n- `IMAGE_PREVIEW_THUMBNAILER_USERAGENT` (optional, default: `pelican-plugin-image-preview-thumbnailer`) :\n  the `User-Agent` HTTP header to use while sending notifications.\n\n### Features that could be implemented\n* the initial idea for this plugin was to just add `🖼️` icons on links to images,\n  and then only display thumbnails when hovering on those links.\n  A more basic approach of just inserting `<img>` tags was in the end deemed sufficient,\n  but the original mechanism could still be implemented with a custom `DEFAULT_INSERTED_HTML` & adequate CSS styling.\n\n## Contributing\nContributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation,\nadding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues](https://github.com/pelican-plugins/image-preview-thumbnailer/issues).\n\nTo start contributing to this plugin, review the [Contributing to Pelican](https://docs.getpelican.com/en/latest/contribute.html) documentation,\nbeginning with the **Contributing Code** section.\n\n### Releasing a new version\nWith a valid `~/.pypirc`:\n\n1. update `CHANGELOG.md`\n2. bump version in `pyproject.toml`\n3. `poetry build && poetry publish`\n4. perform a release on GitGub, including the description added to `CHANGELOG.md`\n\n## Linter & tests\nTo execute them:\n\n    pylint *.py\n    pytest\n',
    'author': 'Lucas Cimon',
    'author_email': 'lucas.cimon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pelican-plugins/image-preview-thumbnailer',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
